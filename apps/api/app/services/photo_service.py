import os
import uuid
import shutil
from typing import Optional
from sqlalchemy.orm import Session as DBSession

from app.models.photo import Photo
from app.models.profile import Profile
from app.services.openai_service import OpenAIServiceProtocol

import tempfile

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", os.path.join(tempfile.gettempdir(), "yellow_uploads"))
MAX_PHOTOS = 3
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


class PhotoService:
    def __init__(self, db: DBSession, openai_service: OpenAIServiceProtocol):
        self.db = db
        self.openai_service = openai_service

    def get_user_photos(self, user_id) -> list[Photo]:
        return (
            self.db.query(Photo)
            .filter_by(user_id=user_id)
            .order_by(Photo.order)
            .all()
        )

    def get_photo(self, photo_id) -> Optional[Photo]:
        return self.db.query(Photo).filter_by(id=photo_id).first()

    def get_photo_count(self, user_id) -> int:
        return self.db.query(Photo).filter_by(user_id=user_id).count()

    def save_photo(self, user_id, file_content: bytes, original_name: str) -> Photo:
        ext = original_name.rsplit(".", 1)[-1].lower() if "." in original_name else "jpg"
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"File type .{ext} not allowed. Use JPEG or PNG.")

        if len(file_content) > MAX_FILE_SIZE:
            raise ValueError("File too large. Maximum 5MB.")

        count = self.get_photo_count(user_id)
        if count >= MAX_PHOTOS:
            raise ValueError(f"Maximum {MAX_PHOTOS} photos allowed.")

        filename = f"{uuid.uuid4()}.{ext}"
        user_dir = os.path.join(UPLOAD_DIR, str(user_id))
        os.makedirs(user_dir, exist_ok=True)

        filepath = os.path.join(user_dir, filename)
        with open(filepath, "wb") as f:
            f.write(file_content)

        try:
            analysis = self.openai_service.analyze_photo(filepath)
        except Exception:
            analysis = {"vibe_description": "", "vibe_tags": []}

        photo = Photo(
            user_id=user_id,
            filename=filename,
            original_name=original_name,
            vibe_description=analysis.get("vibe_description", ""),
            vibe_tags=analysis.get("vibe_tags", []),
            order=count,
        )
        self.db.add(photo)
        self.db.commit()
        self.db.refresh(photo)

        self._update_profile_vibes(user_id)

        return photo

    def delete_photo(self, photo_id, user_id) -> bool:
        photo = self.db.query(Photo).filter_by(id=photo_id, user_id=user_id).first()
        if not photo:
            return False

        filepath = os.path.join(UPLOAD_DIR, str(user_id), photo.filename)
        if os.path.exists(filepath):
            os.remove(filepath)

        self.db.delete(photo)
        self.db.commit()

        self._reorder_photos(user_id)
        self._update_profile_vibes(user_id)

        return True

    def get_file_path(self, photo: Photo) -> str:
        return os.path.join(UPLOAD_DIR, str(photo.user_id), photo.filename)

    def _reorder_photos(self, user_id):
        photos = self.get_user_photos(user_id)
        for i, photo in enumerate(photos):
            photo.order = i
        self.db.commit()

    def _update_profile_vibes(self, user_id):
        """Aggregate vibe_tags from all photos into profile."""
        photos = self.get_user_photos(user_id)
        all_tags = []
        for photo in photos:
            if photo.vibe_tags:
                all_tags.extend(photo.vibe_tags)

        # Deduplicate preserving frequency-based order
        seen = {}
        for tag in all_tags:
            seen[tag] = seen.get(tag, 0) + 1
        unique_tags = sorted(seen.keys(), key=lambda t: -seen[t])

        profile = self.db.query(Profile).filter_by(user_id=user_id).first()
        if profile:
            profile.vibe_tags = unique_tags
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(profile, "vibe_tags")
            self.db.commit()

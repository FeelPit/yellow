from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session as DBSession
from uuid import UUID

from app.database import get_db
from app.routers.auth import get_current_user
from app.models.user import User
from app.services.photo_service import PhotoService
from app.services.openai_service import OpenAIService
from app.schemas.photo import PhotoResponse, PhotoUploadResponse

router = APIRouter(prefix="/api/v1/photos", tags=["photos"])


def get_openai_service() -> OpenAIService:
    return OpenAIService()


@router.post("/upload", response_model=PhotoUploadResponse)
async def upload_photo(
    file: UploadFile = File(...),
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    openai_service: OpenAIService = Depends(get_openai_service),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed.")

    content = await file.read()
    svc = PhotoService(db, openai_service)

    try:
        photo = svc.save_photo(current_user.id, content, file.filename or "photo.jpg")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    tags_str = ", ".join(photo.vibe_tags) if photo.vibe_tags else "analyzing"
    msg = f"Got it! I see a {tags_str} vibe. Nice!"

    return PhotoUploadResponse(
        photo=PhotoResponse.model_validate(photo),
        message=msg,
    )


@router.get("", response_model=list[PhotoResponse])
async def list_photos(
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    openai_service: OpenAIService = Depends(get_openai_service),
):
    svc = PhotoService(db, openai_service)
    return [PhotoResponse.model_validate(p) for p in svc.get_user_photos(current_user.id)]


@router.delete("/{photo_id}", status_code=204)
async def delete_photo(
    photo_id: UUID,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    openai_service: OpenAIService = Depends(get_openai_service),
):
    svc = PhotoService(db, openai_service)
    if not svc.delete_photo(photo_id, current_user.id):
        raise HTTPException(status_code=404, detail="Photo not found")


@router.get("/{photo_id}/file")
async def serve_photo(
    photo_id: UUID,
    db: DBSession = Depends(get_db),
    openai_service: OpenAIService = Depends(get_openai_service),
):
    svc = PhotoService(db, openai_service)
    photo = svc.get_photo(photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    filepath = svc.get_file_path(photo)
    import os
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found on disk")

    ext = photo.filename.rsplit(".", 1)[-1].lower()
    media_type = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
    return FileResponse(filepath, media_type=media_type)


@router.get("/user/{user_id}", response_model=list[PhotoResponse])
async def list_user_photos(
    user_id: UUID,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    openai_service: OpenAIService = Depends(get_openai_service),
):
    """Get photos of another user (for match cards)."""
    svc = PhotoService(db, openai_service)
    return [PhotoResponse.model_validate(p) for p in svc.get_user_photos(user_id)]

from sqlalchemy.orm import Session as DBSession
from uuid import UUID
from typing import List, Tuple

from app.models.user import User
from app.models.profile import Profile
from app.services.openai_service import TRAIT_KEYS


class MatchingService:
    """Matching service using vector similarity on text-based trait insights."""

    def __init__(self, db: DBSession, vector_service=None):
        self.db = db
        self.vector_service = vector_service

    def get_matches(self, user_id: UUID, limit: int = 5) -> List[Tuple[User, Profile, float, str]]:
        current_profile = self.db.query(Profile).filter_by(user_id=user_id).first()
        if not current_profile:
            return []

        profile_text = self._build_profile_text(current_profile)
        if not profile_text:
            return []

        # Try vector similarity first
        vector_ranked = []
        if self.vector_service:
            vector_ranked = self.vector_service.find_similar_profiles(
                str(user_id), profile_text, n_results=20
            )

        all_candidates = self.db.query(User, Profile).join(
            Profile, User.id == Profile.user_id
        ).filter(
            User.id != user_id
        ).all()

        # Filter by gender preference
        filtered = {}
        for user, profile in all_candidates:
            if self._matches_gender_preference(current_profile, profile):
                filtered[str(user.id)] = (user, profile)

        results = []

        if vector_ranked:
            for uid, distance in vector_ranked:
                if uid in filtered:
                    user, profile = filtered[uid]
                    score = max(0.0, 1.0 - distance)
                    explanation = self._generate_explanation(current_profile, profile)
                    results.append((user, profile, round(score, 2), explanation))
                    if len(results) >= limit:
                        break
        else:
            # Fallback: score all candidates by trait overlap
            for uid, (user, profile) in filtered.items():
                score = self._text_similarity_score(current_profile, profile)
                explanation = self._generate_explanation(current_profile, profile)
                results.append((user, profile, round(score, 2), explanation))
            results.sort(key=lambda x: x[2], reverse=True)

        return results[:limit]

    def _build_profile_text(self, profile: Profile) -> str:
        parts = []
        traits = profile.metrics or {}
        for key in TRAIT_KEYS:
            val = traits.get(key)
            if val:
                parts.append(f"{key}: {val}")
        for field in ["communication_style", "attachment_style", "partner_preferences", "values"]:
            val = getattr(profile, field, None)
            if val:
                parts.append(f"{field}: {val}")
        if profile.vibe_tags:
            parts.append(f"vibe: {', '.join(profile.vibe_tags)}")
        return " | ".join(parts)

    def _matches_gender_preference(self, my_profile: Profile, their_profile: Profile) -> bool:
        # If I specified who I'm looking for, they must match
        if my_profile.looking_for and my_profile.looking_for != "any":
            if not their_profile.gender or their_profile.gender != my_profile.looking_for:
                return False

        # If they specified who they're looking for, I must match
        if their_profile.looking_for and their_profile.looking_for != "any":
            if not my_profile.gender or my_profile.gender != their_profile.looking_for:
                return False

        return True

    def _generate_explanation(self, profile1: Profile, profile2: Profile) -> str:
        """Generate a match explanation based on shared trait insights."""
        traits1 = profile1.metrics or {}
        traits2 = profile2.metrics or {}
        shared = []

        for key in TRAIT_KEYS:
            v1, v2 = traits1.get(key), traits2.get(key)
            if v1 and v2:
                shared.append(key.replace("_", " "))

        if len(shared) >= 3:
            return f"You share similar perspectives on {shared[0]}, {shared[1]}, and {shared[2]}."
        elif len(shared) >= 1:
            return f"You have compatible {' and '.join(shared)} patterns."
        else:
            p1_vals = profile1.values or ""
            p2_vals = profile2.values or ""
            if p1_vals and p2_vals:
                return "You both have clearly defined values and know what you're looking for."
            return "You both are looking for meaningful connections."

    def _text_similarity_score(self, profile1: Profile, profile2: Profile) -> float:
        """Fallback: simple count of how many trait dimensions both have filled in, as a proxy."""
        traits1 = profile1.metrics or {}
        traits2 = profile2.metrics or {}
        shared_count = 0
        total = 0
        for key in TRAIT_KEYS:
            v1, v2 = traits1.get(key), traits2.get(key)
            if v1 and v2:
                shared_count += 1
            if v1 or v2:
                total += 1

        text_fields = ["communication_style", "attachment_style", "partner_preferences", "values"]
        for field in text_fields:
            v1 = getattr(profile1, field, None)
            v2 = getattr(profile2, field, None)
            if v1 and v2:
                shared_count += 1
            if v1 or v2:
                total += 1

        return (shared_count / max(total, 1)) * 0.85 + 0.15

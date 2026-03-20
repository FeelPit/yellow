from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import and_
from uuid import UUID

from app.database import get_db
from app.models.like import Like
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.likes import LikeResponse, LikeStatusResponse, MutualLikeResponse

router = APIRouter(prefix="/api/v1/likes", tags=["likes"])


@router.post("/{target_user_id}", response_model=LikeResponse)
def like_user(
    target_user_id: UUID,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id == target_user_id:
        raise HTTPException(status_code=400, detail="Cannot like yourself")

    target = db.query(User).filter_by(id=target_user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    existing = db.query(Like).filter_by(
        user_id=current_user.id, liked_user_id=target_user_id
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Already liked")

    like = Like(user_id=current_user.id, liked_user_id=target_user_id)
    db.add(like)
    db.commit()
    db.refresh(like)
    return like


@router.delete("/{target_user_id}", status_code=204)
def unlike_user(
    target_user_id: UUID,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    like = db.query(Like).filter_by(
        user_id=current_user.id, liked_user_id=target_user_id
    ).first()
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")

    db.delete(like)
    db.commit()


@router.get("/{target_user_id}/status", response_model=LikeStatusResponse)
def get_like_status(
    target_user_id: UUID,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    i_liked = db.query(Like).filter_by(
        user_id=current_user.id, liked_user_id=target_user_id
    ).first() is not None

    they_liked = db.query(Like).filter_by(
        user_id=target_user_id, liked_user_id=current_user.id
    ).first() is not None

    return LikeStatusResponse(liked=i_liked, mutual=i_liked and they_liked)


@router.get("/mutual", response_model=list[MutualLikeResponse])
def get_mutual_likes(
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all users where like is mutual."""
    from sqlalchemy import select
    my_likes = select(Like.liked_user_id).where(Like.user_id == current_user.id).scalar_subquery()
    mutual = (
        db.query(User)
        .join(Like, and_(Like.user_id == User.id, Like.liked_user_id == current_user.id))
        .filter(User.id.in_(my_likes))
        .all()
    )
    return [MutualLikeResponse(user_id=u.id, username=u.username) for u in mutual]

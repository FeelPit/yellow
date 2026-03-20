from pydantic import BaseModel, Field
from uuid import UUID


class SessionCreateRequest(BaseModel):
    user_id: str = Field(..., min_length=1)


class SessionCreateResponse(BaseModel):
    session_id: UUID
    status: str

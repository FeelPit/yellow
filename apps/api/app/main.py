from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health, assistant, profile, auth, matches, likes, conversations, photos

app = FastAPI(title="Yellow API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check at root
app.include_router(health.router, tags=["health"])

# API v1 health
@app.get("/api/v1/health")
async def api_v1_health() -> dict[str, str]:
    return {"status": "ok"}

# Auth routes
app.include_router(auth.router)

# Assistant routes
app.include_router(assistant.router)

# Profile routes
app.include_router(profile.router)

# Matches routes
app.include_router(matches.router)

# Likes routes
app.include_router(likes.router)

# Conversations routes
app.include_router(conversations.router)

# Photos routes
app.include_router(photos.router)

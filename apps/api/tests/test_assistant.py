import uuid


def test_create_session_success(client, db_session, test_user, auth_headers):
    """Test creating a session with authentication."""
    response = client.post(
        "/api/v1/assistant/session",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "status" in data
    assert data["status"] == "created"
    
    # Validate UUID format
    try:
        uuid.UUID(data["session_id"])
    except ValueError:
        pytest.fail("session_id is not a valid UUID")
    
    # Verify session was created in database
    user, _ = test_user
    from app.models.session import Session
    session = db_session.query(Session).filter_by(user_id=user.id).first()
    assert session is not None
    assert str(session.id) == data["session_id"]
    assert session.user_id == user.id
    assert session.created_at is not None


def test_create_session_no_auth(client):
    """Test creating session without authentication."""
    response = client.post("/api/v1/assistant/session")
    
    assert response.status_code == 403


def test_create_session_invalid_token(client):
    """Test creating session with invalid token."""
    response = client.post(
        "/api/v1/assistant/session",
        headers={"Authorization": "Bearer invalid-token"}
    )
    
    assert response.status_code == 401


def test_get_or_create_session(client, test_user, auth_headers):
    """Test getting or creating user session."""
    response = client.get(
        "/api/v1/assistant/session",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["status"] == "created"

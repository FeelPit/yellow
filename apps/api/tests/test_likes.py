import uuid
from app.services.auth_service import AuthService


def _create_other_user(db_session, suffix="other"):
    auth = AuthService(db_session)
    return auth.create_user(
        email=f"{suffix}@example.com",
        username=suffix,
        password="password123"
    )


def test_like_user_success(client, db_session, test_user, auth_headers):
    user, _ = test_user
    other = _create_other_user(db_session)

    response = client.post(f"/api/v1/likes/{other.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(user.id)
    assert data["liked_user_id"] == str(other.id)


def test_like_duplicate(client, db_session, test_user, auth_headers):
    other = _create_other_user(db_session)
    client.post(f"/api/v1/likes/{other.id}", headers=auth_headers)

    response = client.post(f"/api/v1/likes/{other.id}", headers=auth_headers)
    assert response.status_code == 409


def test_like_self(client, test_user, auth_headers):
    user, _ = test_user
    response = client.post(f"/api/v1/likes/{user.id}", headers=auth_headers)
    assert response.status_code == 400


def test_unlike(client, db_session, test_user, auth_headers):
    other = _create_other_user(db_session)
    client.post(f"/api/v1/likes/{other.id}", headers=auth_headers)

    response = client.delete(f"/api/v1/likes/{other.id}", headers=auth_headers)
    assert response.status_code == 204


def test_unlike_nonexistent(client, db_session, test_user, auth_headers):
    other = _create_other_user(db_session)
    response = client.delete(f"/api/v1/likes/{other.id}", headers=auth_headers)
    assert response.status_code == 404


def test_like_status(client, db_session, test_user, auth_headers):
    other = _create_other_user(db_session)

    response = client.get(f"/api/v1/likes/{other.id}/status", headers=auth_headers)
    data = response.json()
    assert data["liked"] is False
    assert data["mutual"] is False

    client.post(f"/api/v1/likes/{other.id}", headers=auth_headers)
    response = client.get(f"/api/v1/likes/{other.id}/status", headers=auth_headers)
    data = response.json()
    assert data["liked"] is True
    assert data["mutual"] is False


def test_mutual_like(client, db_session, test_user, auth_headers):
    user, _ = test_user
    auth = AuthService(db_session)
    other = auth.create_user(email="mutual@example.com", username="mutual", password="password123")
    other_token = auth.create_access_token(other.id)
    other_headers = {"Authorization": f"Bearer {other_token}"}

    client.post(f"/api/v1/likes/{other.id}", headers=auth_headers)
    client.post(f"/api/v1/likes/{user.id}", headers=other_headers)

    response = client.get(f"/api/v1/likes/{other.id}/status", headers=auth_headers)
    data = response.json()
    assert data["liked"] is True
    assert data["mutual"] is True


def test_mutual_likes_list(client, db_session, test_user, auth_headers):
    user, _ = test_user
    auth = AuthService(db_session)
    other = auth.create_user(email="mutual2@example.com", username="mutual2", password="password123")
    other_token = auth.create_access_token(other.id)
    other_headers = {"Authorization": f"Bearer {other_token}"}

    client.post(f"/api/v1/likes/{other.id}", headers=auth_headers)
    client.post(f"/api/v1/likes/{user.id}", headers=other_headers)

    response = client.get("/api/v1/likes/mutual", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["username"] == "mutual2"

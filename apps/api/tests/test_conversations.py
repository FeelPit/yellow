from app.services.auth_service import AuthService
from app.models.subscription import Subscription
from datetime import datetime, timedelta


def _setup_two_users(db_session, test_user):
    user, _ = test_user
    auth = AuthService(db_session)
    other = auth.create_user(email="target@example.com", username="target", password="password123")
    other_token = auth.create_access_token(other.id)
    return user, other, {"Authorization": f"Bearer {other_token}"}


def test_subscription_status_free(client, test_user, auth_headers):
    response = client.get("/api/v1/subscription", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["active"] is False
    assert data["free_chats_remaining"] == 1


def test_access_check_free_message(client, db_session, test_user, auth_headers):
    _, other, _ = _setup_two_users(db_session, test_user)

    response = client.get(f"/api/v1/conversations/{other.id}/access", headers=auth_headers)
    data = response.json()
    assert data["can_message"] is True
    assert data["reason"] == "free_message"


def test_access_check_blocked_after_free(client, db_session, test_user, auth_headers):
    user, other, _ = _setup_two_users(db_session, test_user)

    client.post(f"/api/v1/conversations/{other.id}", headers=auth_headers)

    auth = AuthService(db_session)
    third = auth.create_user(email="third@example.com", username="third", password="password123")

    response = client.get(f"/api/v1/conversations/{third.id}/access", headers=auth_headers)
    data = response.json()
    assert data["can_message"] is False
    assert data["reason"] == "blocked"


def test_access_check_mutual_like(client, db_session, test_user, auth_headers):
    user, other, other_headers = _setup_two_users(db_session, test_user)

    # Use free message first
    auth = AuthService(db_session)
    filler = auth.create_user(email="filler@example.com", username="filler", password="password123")
    client.post(f"/api/v1/conversations/{filler.id}", headers=auth_headers)

    # Now set up mutual like
    client.post(f"/api/v1/likes/{other.id}", headers=auth_headers)
    client.post(f"/api/v1/likes/{user.id}", headers=other_headers)

    response = client.get(f"/api/v1/conversations/{other.id}/access", headers=auth_headers)
    data = response.json()
    assert data["can_message"] is True
    assert data["reason"] == "mutual_like"


def test_access_check_subscription(client, db_session, test_user, auth_headers):
    user, other, _ = _setup_two_users(db_session, test_user)

    # Use free message
    auth = AuthService(db_session)
    filler = auth.create_user(email="filler2@example.com", username="filler2", password="password123")
    client.post(f"/api/v1/conversations/{filler.id}", headers=auth_headers)

    # Create subscription
    sub = Subscription(user_id=user.id, plan="premium", active=True)
    db_session.add(sub)
    db_session.commit()

    response = client.get(f"/api/v1/conversations/{other.id}/access", headers=auth_headers)
    data = response.json()
    assert data["can_message"] is True
    assert data["reason"] == "subscription"


def test_start_conversation_free(client, db_session, test_user, auth_headers):
    _, other, _ = _setup_two_users(db_session, test_user)

    response = client.post(f"/api/v1/conversations/{other.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["other_username"] == "target"
    assert data["access_reason"] == "free_message"


def test_start_conversation_blocked(client, db_session, test_user, auth_headers):
    _, other, _ = _setup_two_users(db_session, test_user)

    client.post(f"/api/v1/conversations/{other.id}", headers=auth_headers)

    auth = AuthService(db_session)
    third = auth.create_user(email="blocked@example.com", username="blocked", password="password123")

    response = client.post(f"/api/v1/conversations/{third.id}", headers=auth_headers)
    assert response.status_code == 403


def test_start_conversation_idempotent(client, db_session, test_user, auth_headers):
    _, other, _ = _setup_two_users(db_session, test_user)

    r1 = client.post(f"/api/v1/conversations/{other.id}", headers=auth_headers)
    r2 = client.post(f"/api/v1/conversations/{other.id}", headers=auth_headers)
    assert r1.json()["id"] == r2.json()["id"]


def test_send_direct_message(client, db_session, test_user, auth_headers):
    _, other, _ = _setup_two_users(db_session, test_user)

    conv = client.post(f"/api/v1/conversations/{other.id}", headers=auth_headers).json()

    response = client.post(
        f"/api/v1/conversations/{conv['id']}/messages",
        json={"content": "Hello!"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Hello!"


def test_get_conversation_messages(client, db_session, test_user, auth_headers):
    user, other, other_headers = _setup_two_users(db_session, test_user)

    conv = client.post(f"/api/v1/conversations/{other.id}", headers=auth_headers).json()
    conv_id = conv["id"]

    client.post(f"/api/v1/conversations/{conv_id}/messages", json={"content": "Hi"}, headers=auth_headers)
    client.post(f"/api/v1/conversations/{conv_id}/messages", json={"content": "Hello"}, headers=other_headers)

    response = client.get(f"/api/v1/conversations/{conv_id}/messages", headers=auth_headers)
    assert response.status_code == 200
    msgs = response.json()
    assert len(msgs) == 2
    assert msgs[0]["content"] == "Hi"
    assert msgs[1]["content"] == "Hello"


def test_list_conversations(client, db_session, test_user, auth_headers):
    _, other, _ = _setup_two_users(db_session, test_user)

    client.post(f"/api/v1/conversations/{other.id}", headers=auth_headers)

    response = client.get("/api/v1/conversations", headers=auth_headers)
    assert response.status_code == 200
    convs = response.json()
    assert len(convs) == 1
    assert convs[0]["other_username"] == "target"


def test_subscription_status_with_premium(client, db_session, test_user, auth_headers):
    user, _ = test_user
    sub = Subscription(
        user_id=user.id, plan="premium", active=True,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db_session.add(sub)
    db_session.commit()

    response = client.get("/api/v1/subscription", headers=auth_headers)
    data = response.json()
    assert data["active"] is True
    assert data["plan"] == "premium"

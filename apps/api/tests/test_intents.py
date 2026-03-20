def test_detect_intent_photo_manage(client, test_session, auth_headers):
    """Test that messages about photos trigger photo_manage intent."""
    client.post(
        f"/api/v1/assistant/session/{test_session}/start",
        headers=auth_headers
    )

    response = client.post(
        f"/api/v1/assistant/session/{test_session}/message",
        json={"content": "I want to change my photo"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "photo_manage"
    assert "camera button" in data["assistant_message"]["content"].lower() or "photo" in data["assistant_message"]["content"].lower()


def test_detect_intent_view_profile(client, test_session, auth_headers):
    """Test that messages about profile trigger view_profile intent."""
    client.post(
        f"/api/v1/assistant/session/{test_session}/start",
        headers=auth_headers
    )

    # First send a normal message to create a profile
    client.post(
        f"/api/v1/assistant/session/{test_session}/message",
        json={"content": "I'm 25, male, looking for female"},
        headers=auth_headers
    )

    response = client.post(
        f"/api/v1/assistant/session/{test_session}/message",
        json={"content": "Show my profile please"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "view_profile"
    assert data["profile_view"] is not None
    assert "photos" in data["profile_view"]


def test_detect_intent_normal(client, test_session, auth_headers):
    """Test that normal messages have null intent."""
    client.post(
        f"/api/v1/assistant/session/{test_session}/start",
        headers=auth_headers
    )

    response = client.post(
        f"/api/v1/assistant/session/{test_session}/message",
        json={"content": "I enjoy reading books in my free time"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] is None


def test_intent_response_has_correct_fields(client, test_session, auth_headers):
    """Test that SendMessageResponse always includes intent and profile_view fields."""
    client.post(
        f"/api/v1/assistant/session/{test_session}/start",
        headers=auth_headers
    )

    response = client.post(
        f"/api/v1/assistant/session/{test_session}/message",
        json={"content": "Hello, I love music"},
        headers=auth_headers
    )
    data = response.json()
    assert "intent" in data
    assert "profile_view" in data

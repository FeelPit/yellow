import uuid


def test_get_profile_success(client, test_session, auth_headers):
    """Test getting profile after messages are sent."""
    client.post(
        f"/api/v1/assistant/session/{test_session}/start",
        headers=auth_headers
    )

    for i in range(5):
        client.post(
            f"/api/v1/assistant/session/{test_session}/message",
            json={"content": f"Answer {i+1}"},
            headers=auth_headers
        )

    response = client.get(
        f"/api/v1/profile/{test_session}",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert "communication_style" in data
    assert "attachment_style" in data
    assert "partner_preferences" in data
    assert "values" in data
    assert "metrics" in data


def test_get_profile_not_found(client, test_session, auth_headers):
    """Test getting profile for session without conversation returns 404."""
    response = client.get(
        f"/api/v1/profile/{test_session}",
        headers=auth_headers
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_profile_invalid_session(client, auth_headers):
    """Test getting profile for invalid session returns 404."""
    fake_session_id = str(uuid.uuid4())
    response = client.get(
        f"/api/v1/profile/{fake_session_id}",
        headers=auth_headers
    )

    assert response.status_code == 404


def test_profile_structure_with_traits(client, test_session, auth_headers):
    """Test that profile has traits as text insights, not numbers."""
    client.post(
        f"/api/v1/assistant/session/{test_session}/start",
        headers=auth_headers
    )

    for i in range(5):
        client.post(
            f"/api/v1/assistant/session/{test_session}/message",
            json={"content": f"Answer {i+1}"},
            headers=auth_headers
        )

    response = client.get(
        f"/api/v1/profile/{test_session}",
        headers=auth_headers
    )

    data = response.json()

    assert isinstance(data["communication_style"], str)
    assert len(data["communication_style"]) > 0
    assert len(data["values"]) > 0

    metrics = data["metrics"]
    assert metrics is not None
    assert "openness" in metrics

    # Traits should be text strings, not numbers
    openness = metrics["openness"]
    assert isinstance(openness, str)
    assert len(openness) > 5


def test_profile_traits_evolve(client, test_session, auth_headers):
    """Test that profile traits fill in progressively."""
    client.post(
        f"/api/v1/assistant/session/{test_session}/start",
        headers=auth_headers
    )

    client.post(
        f"/api/v1/assistant/session/{test_session}/message",
        json={"content": "I'm 25, male"},
        headers=auth_headers
    )

    response1 = client.get(
        f"/api/v1/profile/{test_session}",
        headers=auth_headers
    )
    traits1 = response1.json()["metrics"]
    filled1 = sum(1 for v in traits1.values() if v is not None)

    for i in range(3):
        client.post(
            f"/api/v1/assistant/session/{test_session}/message",
            json={"content": f"More about me {i+1}"},
            headers=auth_headers
        )

    response2 = client.get(
        f"/api/v1/profile/{test_session}",
        headers=auth_headers
    )
    traits2 = response2.json()["metrics"]
    filled2 = sum(1 for v in traits2.values() if v is not None)

    assert filled2 > filled1

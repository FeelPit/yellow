import uuid


def test_start_conversation_success(client, test_session, auth_headers):
    """Test starting a conversation returns 1 initial question."""
    response = client.post(
        f"/api/v1/assistant/session/{test_session}/start",
        headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()
    assert "messages" in data
    assert len(data["messages"]) == 1

    msg = data["messages"][0]
    assert msg["role"] == "assistant"
    assert msg["session_id"] == test_session
    assert "content" in msg
    assert "id" in msg
    assert "created_at" in msg


def test_start_conversation_invalid_session(client, auth_headers):
    """Test starting conversation with invalid session returns 404."""
    fake_session_id = str(uuid.uuid4())
    response = client.post(
        f"/api/v1/assistant/session/{fake_session_id}/start",
        headers=auth_headers
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_start_conversation_idempotent(client, test_session, auth_headers):
    """Test starting conversation twice returns same messages."""
    response1 = client.post(
        f"/api/v1/assistant/session/{test_session}/start",
        headers=auth_headers
    )
    messages1 = response1.json()["messages"]

    response2 = client.post(
        f"/api/v1/assistant/session/{test_session}/start",
        headers=auth_headers
    )
    messages2 = response2.json()["messages"]

    assert len(messages1) == len(messages2)
    for msg1, msg2 in zip(messages1, messages2):
        assert msg1["id"] == msg2["id"]
        assert msg1["content"] == msg2["content"]


def test_send_message_success(client, test_session, auth_headers):
    """Test sending a message returns response with profile snapshot."""
    client.post(
        f"/api/v1/assistant/session/{test_session}/start",
        headers=auth_headers
    )

    response = client.post(
        f"/api/v1/assistant/session/{test_session}/message",
        json={"content": "I love hiking"},
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert "user_message" in data
    assert "assistant_message" in data
    assert "profile_ready" in data
    assert "profile_snapshot" in data

    user_msg = data["user_message"]
    assert user_msg["role"] == "user"
    assert user_msg["content"] == "I love hiking"

    assistant_msg = data["assistant_message"]
    assert assistant_msg["role"] == "assistant"
    assert len(assistant_msg["content"]) > 0
    assert "thinking" in assistant_msg

    snapshot = data["profile_snapshot"]
    assert snapshot is not None
    assert "metrics" in snapshot
    assert snapshot["metrics"]["openness"] is not None
    assert isinstance(snapshot["metrics"]["openness"], str)


def test_send_message_invalid_session(client, auth_headers):
    """Test sending message to invalid session returns 404."""
    fake_session_id = str(uuid.uuid4())
    response = client.post(
        f"/api/v1/assistant/session/{fake_session_id}/message",
        json={"content": "Hello"},
        headers=auth_headers
    )
    assert response.status_code == 404


def test_send_message_empty_content(client, test_session, auth_headers):
    """Test sending empty message returns 422."""
    response = client.post(
        f"/api/v1/assistant/session/{test_session}/message",
        json={"content": ""},
        headers=auth_headers
    )
    assert response.status_code == 422


def test_profile_evolves_with_messages(client, test_session, auth_headers):
    """Test that profile traits evolve after each message."""
    client.post(
        f"/api/v1/assistant/session/{test_session}/start",
        headers=auth_headers
    )

    snapshots = []
    for i in range(5):
        response = client.post(
            f"/api/v1/assistant/session/{test_session}/message",
            json={"content": f"Message {i+1}"},
            headers=auth_headers
        )
        data = response.json()
        snapshots.append(data["profile_snapshot"])

        if i < 4:
            assert data["profile_ready"] is False
        else:
            assert data["profile_ready"] is True

    # First snapshot should have fewer traits than last
    traits_1 = snapshots[0]["metrics"]
    traits_5 = snapshots[4]["metrics"]
    filled_1 = sum(1 for v in traits_1.values() if v is not None)
    filled_5 = sum(1 for v in traits_5.values() if v is not None)
    assert filled_5 > filled_1

    # All trait values should be strings
    for v in traits_5.values():
        if v is not None:
            assert isinstance(v, str)


def test_thinking_in_assistant_messages(client, test_session, auth_headers):
    """Test that assistant messages include thinking."""
    client.post(
        f"/api/v1/assistant/session/{test_session}/start",
        headers=auth_headers
    )

    response = client.post(
        f"/api/v1/assistant/session/{test_session}/message",
        json={"content": "I'm 25, male, looking for someone special"},
        headers=auth_headers
    )

    data = response.json()
    assistant_msg = data["assistant_message"]
    assert assistant_msg["thinking"] is not None
    assert len(assistant_msg["thinking"]) > 0


def test_get_messages_chronological(client, test_session, auth_headers):
    """Test getting messages returns them in chronological order."""
    client.post(
        f"/api/v1/assistant/session/{test_session}/start",
        headers=auth_headers
    )

    client.post(
        f"/api/v1/assistant/session/{test_session}/message",
        json={"content": "Test message"},
        headers=auth_headers
    )

    response = client.get(
        f"/api/v1/assistant/session/{test_session}/messages",
        headers=auth_headers
    )
    assert response.status_code == 200

    messages = response.json()
    assert len(messages) == 3

    assert messages[0]["role"] == "assistant"
    assert messages[1]["role"] == "user"
    assert messages[2]["role"] == "assistant"


def test_get_messages_invalid_session(client, auth_headers):
    """Test getting messages for invalid session returns 404."""
    fake_session_id = str(uuid.uuid4())
    response = client.get(
        f"/api/v1/assistant/session/{fake_session_id}/messages",
        headers=auth_headers
    )
    assert response.status_code == 404

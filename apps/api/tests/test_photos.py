import io


def test_upload_photo_success(client, test_session, auth_headers):
    """Test uploading a photo returns analysis results."""
    client.post(
        f"/api/v1/assistant/session/{test_session}/start",
        headers=auth_headers
    )
    # Send one message to create a profile
    client.post(
        f"/api/v1/assistant/session/{test_session}/message",
        json={"content": "I'm 25, male, looking for female"},
        headers=auth_headers
    )

    img_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    response = client.post(
        "/api/v1/photos/upload",
        headers={"Authorization": auth_headers["Authorization"]},
        files={"file": ("test.png", io.BytesIO(img_data), "image/png")},
    )
    assert response.status_code == 200
    data = response.json()
    assert "photo" in data
    assert "message" in data
    assert data["photo"]["original_name"] == "test.png"
    assert data["photo"]["vibe_tags"] is not None
    assert len(data["photo"]["vibe_tags"]) > 0


def test_upload_photo_limit(client, test_session, auth_headers):
    """Test that you can't upload more than 3 photos."""
    client.post(
        f"/api/v1/assistant/session/{test_session}/start",
        headers=auth_headers
    )
    client.post(
        f"/api/v1/assistant/session/{test_session}/message",
        json={"content": "I'm 25, male, looking for female"},
        headers=auth_headers
    )

    for i in range(3):
        img_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 50
        response = client.post(
            "/api/v1/photos/upload",
            headers={"Authorization": auth_headers["Authorization"]},
            files={"file": (f"photo{i}.png", io.BytesIO(img_data), "image/png")},
        )
        assert response.status_code == 200

    img_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 50
    response = client.post(
        "/api/v1/photos/upload",
        headers={"Authorization": auth_headers["Authorization"]},
        files={"file": ("photo4.png", io.BytesIO(img_data), "image/png")},
    )
    assert response.status_code == 400
    assert "Maximum" in response.json()["detail"]


def test_list_photos(client, test_session, auth_headers):
    """Test listing user photos."""
    response = client.get(
        "/api/v1/photos",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_delete_photo(client, test_session, auth_headers):
    """Test deleting a photo."""
    client.post(
        f"/api/v1/assistant/session/{test_session}/start",
        headers=auth_headers
    )
    client.post(
        f"/api/v1/assistant/session/{test_session}/message",
        json={"content": "I'm 25, male, looking for female"},
        headers=auth_headers
    )

    img_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 50
    upload_resp = client.post(
        "/api/v1/photos/upload",
        headers={"Authorization": auth_headers["Authorization"]},
        files={"file": ("del.png", io.BytesIO(img_data), "image/png")},
    )
    photo_id = upload_resp.json()["photo"]["id"]

    del_resp = client.delete(
        f"/api/v1/photos/{photo_id}",
        headers=auth_headers,
    )
    assert del_resp.status_code == 204

    # Verify it's gone
    list_resp = client.get("/api/v1/photos", headers=auth_headers)
    ids = [p["id"] for p in list_resp.json()]
    assert photo_id not in ids


def test_delete_nonexistent_photo(client, auth_headers):
    """Test deleting a photo that doesn't exist returns 404."""
    import uuid
    response = client.delete(
        f"/api/v1/photos/{uuid.uuid4()}",
        headers=auth_headers,
    )
    assert response.status_code == 404

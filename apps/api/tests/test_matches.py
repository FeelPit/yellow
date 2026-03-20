import uuid
from app.models.user import User
from app.models.session import Session
from app.models.profile import Profile


def test_get_user_profile_success(client, db_session, test_user, auth_headers):
    """Test getting a user's profile."""
    user, token = test_user
    
    # Create session for test user
    session = Session(user_id=user.id)
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    
    # Create profile for test user
    profile = Profile(
        session_id=session.id,
        user_id=user.id,
        communication_style="Direct and honest",
        attachment_style="Secure",
        partner_preferences="Looking for emotional intelligence",
        values="Values authenticity",
    )
    db_session.add(profile)
    db_session.commit()
    
    response = client.get(
        f"/api/v1/users/{user.id}/profile",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["communication_style"] == "Direct and honest"
    assert data["attachment_style"] == "Secure"


def test_get_user_profile_not_found(client, auth_headers):
    """Test getting profile for user without profile returns 404."""
    fake_user_id = str(uuid.uuid4())
    response = client.get(
        f"/api/v1/users/{fake_user_id}/profile",
        headers=auth_headers
    )
    
    assert response.status_code == 404


def test_get_matches_requires_auth(client, test_user):
    """Test that getting matches requires authentication."""
    user, token = test_user
    # Request without auth headers should return 401
    response = client.get(f"/api/v1/users/{user.id}/matches")
    # FastAPI returns 403 when dependency fails, not 401
    assert response.status_code in [401, 403]


def test_get_matches_empty_when_no_profile(client, test_user, auth_headers):
    """Test getting matches returns empty when user has no profile."""
    user, token = test_user
    response = client.get(
        f"/api/v1/users/{user.id}/matches",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["matches"] == []
    assert data["total"] == 0


def test_get_matches_success(client, db_session, test_user, auth_headers):
    """Test getting matches returns other users with profiles."""
    from app.services.auth_service import AuthService
    
    user, token = test_user
    auth_service = AuthService(db_session)
    
    # Create session for test user
    test_session = Session(user_id=user.id)
    db_session.add(test_session)
    db_session.commit()
    db_session.refresh(test_session)
    
    # Create profile for test user
    test_profile = Profile(
        session_id=test_session.id,
        user_id=user.id,
        communication_style="Direct and honest communicator",
        attachment_style="Secure attachment",
        partner_preferences="Looking for emotional intelligence and authenticity",
        values="Values authenticity and meaningful connections",
    )
    db_session.add(test_profile)
    db_session.commit()
    
    # Create 3 other users with profiles
    for i in range(3):
        match_user = auth_service.create_user(
            email=f"match{i}@example.com",
            username=f"match{i}",
            password="password123"
        )
        
        session = Session(user_id=match_user.id)
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)
        
        profile = Profile(
            session_id=session.id,
            user_id=match_user.id,
            communication_style=f"Communication style {i}",
            attachment_style=f"Attachment style {i}",
            partner_preferences=f"Partner preferences {i} with authenticity",
            values=f"Values {i} and meaningful connections",
        )
        db_session.add(profile)
    
    db_session.commit()
    
    # Get matches
    response = client.get(
        f"/api/v1/users/{user.id}/matches",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["matches"]) == 3
    assert data["total"] == 3
    
    # Verify match structure
    match = data["matches"][0]
    assert "user_id" in match
    assert "username" in match
    assert "profile" in match
    assert "match_score" in match
    assert "match_explanation" in match
    
    # Verify profile structure
    assert "communication_style" in match["profile"]
    assert "attachment_style" in match["profile"]
    assert "partner_preferences" in match["profile"]
    assert "values" in match["profile"]


def test_get_matches_excludes_self(client, db_session, test_user, auth_headers):
    """Test that matches don't include the requesting user."""
    from app.services.auth_service import AuthService
    
    user, token = test_user
    auth_service = AuthService(db_session)
    
    # Create session for test user
    test_session = Session(user_id=user.id)
    db_session.add(test_session)
    db_session.commit()
    db_session.refresh(test_session)
    
    # Create profile for test user
    test_profile = Profile(
        session_id=test_session.id,
        user_id=user.id,
        communication_style="Test style",
        attachment_style="Test attachment",
        partner_preferences="Test preferences",
        values="Test values",
    )
    db_session.add(test_profile)
    db_session.commit()
    
    # Create 2 other users with profiles
    for i in range(2):
        match_user = auth_service.create_user(
            email=f"other{i}@example.com",
            username=f"other{i}",
            password="password123"
        )
        
        session = Session(user_id=match_user.id)
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)
        
        profile = Profile(
            session_id=session.id,
            user_id=match_user.id,
            communication_style=f"Style {i}",
            attachment_style=f"Attachment {i}",
            partner_preferences=f"Preferences {i}",
            values=f"Values {i}",
        )
        db_session.add(profile)
    
    db_session.commit()
    
    # Get matches
    response = client.get(
        f"/api/v1/users/{user.id}/matches",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify test user is not in matches
    match_user_ids = [match["user_id"] for match in data["matches"]]
    assert str(user.id) not in match_user_ids


def test_get_matches_max_5_results(client, db_session, test_user, auth_headers):
    """Test that matches returns maximum 5 results."""
    from app.services.auth_service import AuthService
    
    user, token = test_user
    auth_service = AuthService(db_session)
    
    # Create session for test user
    test_session = Session(user_id=user.id)
    db_session.add(test_session)
    db_session.commit()
    db_session.refresh(test_session)
    
    # Create profile for test user
    test_profile = Profile(
        session_id=test_session.id,
        user_id=user.id,
        communication_style="Test style",
        attachment_style="Test attachment",
        partner_preferences="Test preferences",
        values="Test values",
    )
    db_session.add(test_profile)
    db_session.commit()
    
    # Create 10 other users with profiles
    for i in range(10):
        match_user = auth_service.create_user(
            email=f"many{i}@example.com",
            username=f"many{i}",
            password="password123"
        )
        
        session = Session(user_id=match_user.id)
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)
        
        profile = Profile(
            session_id=session.id,
            user_id=match_user.id,
            communication_style=f"Style {i}",
            attachment_style=f"Attachment {i}",
            partner_preferences=f"Preferences {i}",
            values=f"Values {i}",
        )
        db_session.add(profile)
    
    db_session.commit()
    
    # Get matches
    response = client.get(
        f"/api/v1/users/{user.id}/matches",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["matches"]) == 5
    assert data["total"] == 5


def test_get_matches_only_own_matches(client, db_session, test_user, auth_headers):
    """Test that users can only view their own matches."""
    from app.services.auth_service import AuthService
    
    user, token = test_user
    auth_service = AuthService(db_session)
    
    # Create another user
    other_user = auth_service.create_user(
        email="other@example.com",
        username="other",
        password="password123"
    )
    
    # Try to get other user's matches
    response = client.get(
        f"/api/v1/users/{other_user.id}/matches",
        headers=auth_headers
    )
    
    assert response.status_code == 403


def test_match_explanation_exists(client, db_session, test_user, auth_headers):
    """Test that match explanation is provided."""
    from app.services.auth_service import AuthService
    
    user, token = test_user
    auth_service = AuthService(db_session)
    
    # Create session for test user
    test_session = Session(user_id=user.id)
    db_session.add(test_session)
    db_session.commit()
    db_session.refresh(test_session)
    
    # Create profile for test user
    test_profile = Profile(
        session_id=test_session.id,
        user_id=user.id,
        communication_style="Direct communicator",
        attachment_style="Secure",
        partner_preferences="Emotional intelligence",
        values="Authenticity",
    )
    db_session.add(test_profile)
    db_session.commit()
    
    # Create match with similar profile
    match_user = auth_service.create_user(
        email="match@example.com",
        username="match",
        password="password123"
    )
    
    match_session = Session(user_id=match_user.id)
    db_session.add(match_session)
    db_session.commit()
    db_session.refresh(match_session)
    
    match_profile = Profile(
        session_id=match_session.id,
        user_id=match_user.id,
        communication_style="Direct communicator",
        attachment_style="Secure",
        partner_preferences="Emotional intelligence",
        values="Authenticity",
    )
    db_session.add(match_profile)
    db_session.commit()
    
    # Get matches
    response = client.get(
        f"/api/v1/users/{user.id}/matches",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["matches"]) > 0
    
    match = data["matches"][0]
    assert match["match_explanation"]
    assert len(match["match_explanation"]) > 0
    assert isinstance(match["match_score"], (int, float))
    assert 0.0 <= match["match_score"] <= 1.0

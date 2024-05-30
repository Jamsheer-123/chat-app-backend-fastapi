# test/test_user_profile.py

import sys
import os
import pytest
from fastapi.testclient import TestClient

# Add the project directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

client = TestClient(app)

@pytest.fixture
def test_user():
    return {
        "username": "string",
        "email": "user1@example.com",
        "full_name": "string",
        "password": "string",
        "role": "string",
        "login_type": "string",
        "active": False,
        "verified": False
    }

@pytest.fixture
def auth_token(test_user):
    # Register the user
    response = client.post("/api/auth/register", json=test_user)
    if response.status_code == 409:  # If the user already exists, handle it
        # Login the user directly
        login_response = client.post("/api/auth/login", json={"email": test_user["email"], "password": test_user["password"]})
        assert login_response.status_code == 200, f"Login endpoint failed: {login_response.text}"
        return login_response.json()["access_token"]
    assert response.status_code == 201, f"Register endpoint failed: {response.text}"

    # Simulate OTP verification (adjust according to your verification logic)
    response = client.post("/api/auth/verifyotp?email={}&otp=123456".format(test_user["email"]))
    assert response.status_code == 200, f"OTP verification failed: {response.text}"

    # Login the user
    response = client.post("/api/auth/login", json={"email": test_user["email"], "password": test_user["password"]})
    assert response.status_code == 200, f"Login endpoint failed: {response.text}"
    return response.json()["access_token"]

def test_get_user_profile(auth_token):
    response = client.get("/api/user/profile", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200, f"Get profile endpoint failed: {response.text}"
    data = response.json()
    assert data["username"] == "string"
    assert data["email"] == "user1@example.com"

def test_update_user_profile(auth_token):
    update_data = {
        "full_name": "Test User",
        "bio": "This is a test user.",
        "image": "http://example.com/image.jpg"
    }
    response = client.put("/api/user/profile", json=update_data, headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200, f"Update profile endpoint failed: {response.text}"
    data = response.json()
    assert data["full_name"] == "Test User"
    assert data["bio"] == "This is a test user."
    assert data["image"] == "http://example.com/image.jpg"

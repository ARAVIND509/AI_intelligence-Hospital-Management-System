import pytest


def test_user_registration_and_login(client):
    # 1. Register User
    reg_res = client.post("/api/v1/auth/register", json={
        "username": "johndoe",
        "email": "john@example.com",
        "password": "password123",
        "role": "PATIENT"
    })
    assert reg_res.status_code == 201
    user_data = reg_res.json()["data"]
    assert user_data["username"] == "johndoe"
    assert user_data["role"] == "PATIENT"
    assert "password" not in user_data
    assert "password_hash" not in user_data

    # 2. Duplicate Registration Check
    dup_res = client.post("/api/v1/auth/register", json={
        "username": "johndoe",
        "email": "john@example.com",
        "password": "password123"
    })
    assert dup_res.status_code == 409

    # 3. Invalid Login
    invalid_login = client.post("/api/v1/auth/login", json={
        "username_or_email": "john@example.com",
        "password": "wrongpassword"
    })
    assert invalid_login.status_code == 401

    # 4. Valid Login
    login_res = client.post("/api/v1/auth/login", json={
        "username_or_email": "john@example.com",
        "password": "password123"
    })
    assert login_res.status_code == 200
    token = login_res.json()["data"]["access_token"]
    assert token is not None

    # 5. Access /me with token
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["data"]["email"] == "john@example.com"

    # 6. Change Password
    change_res = client.post("/api/v1/auth/change-password", headers=headers, json={
        "old_password": "password123",
        "new_password": "newpassword456"
    })
    assert change_res.status_code == 200

    # Login with new password
    new_login = client.post("/api/v1/auth/login", json={
        "username_or_email": "john@example.com",
        "password": "newpassword456"
    })
    assert new_login.status_code == 200


def test_missing_or_invalid_token(client):
    # Unauthenticated request
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401

    # Invalid token format
    res_inv = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid_token_123"})
    assert res_inv.status_code == 401

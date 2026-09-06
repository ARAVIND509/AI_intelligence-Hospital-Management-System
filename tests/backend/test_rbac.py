import pytest


def test_rbac_permissions_and_ownership(client):
    # 1. Register Admin User
    admin_reg = client.post("/api/v1/auth/register", json={
        "username": "admin_user",
        "email": "admin@hospital.com",
        "password": "adminpassword",
        "role": "ADMIN"
    })
    admin_token = client.post("/api/v1/auth/login", json={
        "username_or_email": "admin@hospital.com",
        "password": "adminpassword"
    }).json()["data"]["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Admin creates Patient record
    p1_res = client.post("/api/v1/patients/", headers=admin_headers, json={"name": "Patient 1"})
    p1_id = p1_res.json()["data"]["id"]
    p2_res = client.post("/api/v1/patients/", headers=admin_headers, json={"name": "Patient 2"})
    p2_id = p2_res.json()["data"]["id"]

    # 2. Register Patient 1 User (linked to patient 1)
    client.post("/api/v1/auth/register", json={
        "username": "patient1_user",
        "email": "p1@test.com",
        "password": "p1password",
        "role": "PATIENT",
        "patient_id": p1_id
    })
    p1_token = client.post("/api/v1/auth/login", json={
        "username_or_email": "p1@test.com",
        "password": "p1password"
    }).json()["data"]["access_token"]
    p1_headers = {"Authorization": f"Bearer {p1_token}"}

    # 3. Patient 1 tries to access Patient 1 record (Allowed)
    res_p1 = client.get(f"/api/v1/patients/{p1_id}", headers=p1_headers)
    assert res_p1.status_code == 200

    # 4. Patient 1 tries to access Patient 2 record (Forbidden - 403)
    res_p2 = client.get(f"/api/v1/patients/{p2_id}", headers=p1_headers)
    assert res_p2.status_code == 403

    # 5. Patient 1 tries to create Department (Forbidden - 403, requires ADMIN)
    res_dept = client.post("/api/v1/departments/", headers=p1_headers, json={"name": "Cardiology"})
    assert res_dept.status_code == 403

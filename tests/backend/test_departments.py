import pytest


def test_department_crud(client):
    # Create
    res = client.post("/api/v1/departments/", json={
        "name": "Cardiology",
        "description": "Heart and vascular department"
    })
    assert res.status_code == 201
    dept_id = res.json()["data"]["id"]
    assert res.json()["data"]["name"] == "Cardiology"

    # Duplicate name check
    dup_res = client.post("/api/v1/departments/", json={"name": "Cardiology"})
    assert dup_res.status_code == 409

    # Get by ID
    get_res = client.get(f"/api/v1/departments/{dept_id}")
    assert get_res.status_code == 200
    assert get_res.json()["data"]["description"] == "Heart and vascular department"

    # Update
    up_res = client.patch(f"/api/v1/departments/{dept_id}", json={"description": "Updated Heart Center"})
    assert up_res.status_code == 200
    assert up_res.json()["data"]["description"] == "Updated Heart Center"

    # List & Search
    list_res = client.get("/api/v1/departments/?search=Heart")
    assert list_res.status_code == 200
    assert list_res.json()["data"]["total"] == 1

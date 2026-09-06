import pytest


def test_medical_records_crud(client):
    # Setup Patient & Doctor
    p_res = client.post("/api/v1/patients/", json={"name": "Alice Green", "age": 28})
    patient_id = p_res.json()["data"]["id"]
    d_res = client.post("/api/v1/doctors/", json={"name": "Dr. Bob", "specialization": "Neurology"})
    doctor_id = d_res.json()["data"]["id"]

    # Create record
    rec_payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "diagnosis": "Migraine headache",
        "symptoms": "Severe headache, light sensitivity",
        "treatment_plan": "Rest and prescribe pain relievers",
        "notes": "Follow up in 2 weeks"
    }
    create_res = client.post("/api/v1/medical-records/", json=rec_payload)
    assert create_res.status_code == 201
    rec_data = create_res.json()["data"]
    rec_id = rec_data["record_id"]
    assert rec_id == "REC-000001"
    assert rec_data["diagnosis"] == "Migraine headache"

    # Get by ID
    get_res = client.get(f"/api/v1/medical-records/{rec_id}")
    assert get_res.status_code == 200
    assert get_res.json()["data"]["patient"]["name"] == "Alice Green"

    # Update
    up_res = client.patch(f"/api/v1/medical-records/{rec_id}", json={"treatment_plan": "Updated rest and hydration plan"})
    assert up_res.status_code == 200
    assert up_res.json()["data"]["treatment_plan"] == "Updated rest and hydration plan"

    # Patient History
    hist_res = client.get(f"/api/v1/medical-records/patient/{patient_id}")
    assert hist_res.status_code == 200
    assert len(hist_res.json()["data"]) == 1

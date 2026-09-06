import pytest


def test_prescriptions_crud(client, admin_headers):
    p_res = client.post("/api/v1/patients/", headers=admin_headers, json={"name": "Charlie Brown"})
    patient_id = p_res.json()["data"]["id"]
    d_res = client.post("/api/v1/doctors/", headers=admin_headers, json={"name": "Dr. Lucy", "specialization": "Pediatrics"})
    doctor_id = d_res.json()["data"]["id"]

    rx_payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "notes": "Take medicines after food",
        "medicines": [
            {
                "medicine_name": "Amoxicillin",
                "dosage": "500mg",
                "frequency": "Three times daily",
                "duration": "7 days",
                "instructions": "Take with water"
            },
            {
                "medicine_name": "Paracetamol",
                "dosage": "650mg",
                "frequency": "Twice daily",
                "duration": "3 days",
                "instructions": "For fever"
            }
        ]
    }

    create_res = client.post("/api/v1/prescriptions/", headers=admin_headers, json=rx_payload)
    assert create_res.status_code == 201
    rx_data = create_res.json()["data"]
    rx_id = rx_data["rx_id"]
    assert rx_id == "RX-000001"
    assert len(rx_data["medicines"]) == 2

    # Get details
    get_res = client.get(f"/api/v1/prescriptions/{rx_id}", headers=admin_headers)
    assert get_res.status_code == 200
    assert get_res.json()["data"]["medicines"][0]["medicine_name"] == "Amoxicillin"

    # Patient history
    hist_res = client.get(f"/api/v1/prescriptions/patient/{patient_id}", headers=admin_headers)
    assert hist_res.status_code == 200
    assert len(hist_res.json()["data"]) == 1

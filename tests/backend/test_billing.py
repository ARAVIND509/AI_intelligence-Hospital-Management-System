import pytest


def test_billing_crud(client, admin_headers):
    p_res = client.post("/api/v1/patients/", headers=admin_headers, json={"name": "David Miller"})
    patient_id = p_res.json()["data"]["id"]

    bill_payload = {
        "patient_id": patient_id,
        "discount": 50.0,
        "tax": 20.0,
        "payment_method": "card",
        "items": [
            {
                "item_name": "Doctor Consultation Fee",
                "quantity": 1,
                "unit_price": 500.0
            },
            {
                "item_name": "Blood Diagnostic Test",
                "quantity": 2,
                "unit_price": 150.0
            }
        ]
    }

    create_res = client.post("/api/v1/billing/", headers=admin_headers, json=bill_payload)
    assert create_res.status_code == 201
    bill_data = create_res.json()["data"]
    bill_id = bill_data["bill_id"]
    assert bill_id == "INV-000001"
    assert bill_data["total_amount"] == 800.0  # 500 + 300
    assert bill_data["net_amount"] == 770.0    # 800 - 50 + 20
    assert bill_data["payment_status"] == "unpaid"

    # Update payment status
    up_res = client.patch(f"/api/v1/billing/{bill_id}", headers=admin_headers, json={"payment_status": "paid"})
    assert up_res.status_code == 200
    assert up_res.json()["data"]["payment_status"] == "paid"

    # Patient billing history
    hist_res = client.get(f"/api/v1/billing/patient/{patient_id}", headers=admin_headers)
    assert hist_res.status_code == 200
    assert len(hist_res.json()["data"]) == 1

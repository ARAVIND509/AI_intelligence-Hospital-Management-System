import pytest


def test_complete_phase7_end_to_end_workflow(client):
    # 1. Register Department
    dept_res = client.post("/api/v1/departments/", json={
        "name": "Orthopedics",
        "description": "Bone and joint care"
    })
    assert dept_res.status_code == 201
    dept_id = dept_res.json()["data"]["id"]

    # 2. Register Patient
    patient_res = client.post("/api/v1/patients/", json={
        "name": "Bruce Wayne",
        "age": 40,
        "gender": "Male",
        "email": "bruce@gotham.org",
        "phone": "555-0199",
        "address": "Wayne Manor, Gotham",
        "medical_history": "Previous bone fractures"
    })
    assert patient_res.status_code == 201
    patient_id = patient_res.json()["data"]["id"]

    # 3. Register Doctor in Department with availability
    doctor_res = client.post("/api/v1/doctors/", json={
        "name": "Dr. Thomas Elliot",
        "specialization": "Orthopedic Surgery",
        "department_id": dept_id,
        "email": "elliot@hospital.com",
        "phone": "555-0200",
        "working_days": "Monday,Tuesday,Wednesday,Thursday,Friday",
        "working_hours_start": "09:00:00",
        "working_hours_end": "17:00:00",
        "is_active": True,
        "is_available": True
    })
    assert doctor_res.status_code == 201
    doctor_id = doctor_res.json()["data"]["id"]

    # 4. Schedule Appointment
    apt_res = client.post("/api/v1/appointments/", json={
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "appointment_date": "2026-10-05",
        "appointment_time": "10:00:00",
        "reason": "Knee pain examination",
        "notes": "Patient reported acute pain after physical activity"
    })
    assert apt_res.status_code == 201
    apt_id = apt_res.json()["data"]["apt_id"]
    numeric_apt_id = apt_res.json()["data"]["id"]

    # Confirm Appointment
    client.put(f"/api/v1/appointments/{apt_id}", json={"status": "confirmed"})

    # 5. Doctor conducts consultation & creates Medical Record
    rec_res = client.post("/api/v1/medical-records/", json={
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "appointment_id": numeric_apt_id,
        "diagnosis": "Patellar tendinitis",
        "symptoms": "Localized pain below the kneecap",
        "treatment_plan": "Physical therapy and anti-inflammatory medication",
        "notes": "Avoid high-impact exercise for 3 weeks"
    })
    assert rec_res.status_code == 201
    rec_id = rec_res.json()["data"]["record_id"]
    numeric_rec_id = rec_res.json()["data"]["id"]

    # 6. Issue Prescription
    rx_res = client.post("/api/v1/prescriptions/", json={
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "appointment_id": numeric_apt_id,
        "medical_record_id": numeric_rec_id,
        "notes": "Take after meals",
        "medicines": [
            {
                "medicine_name": "Ibuprofen",
                "dosage": "400mg",
                "frequency": "Twice daily",
                "duration": "10 days",
                "instructions": "Take with food"
            }
        ]
    })
    assert rx_res.status_code == 201
    rx_id = rx_res.json()["data"]["rx_id"]

    # 7. Generate Billing & Invoice
    bill_res = client.post("/api/v1/billing/", json={
        "patient_id": patient_id,
        "appointment_id": numeric_apt_id,
        "discount": 20.0,
        "tax": 10.0,
        "payment_method": "card",
        "items": [
            {"item_name": "Orthopedic Consultation Fee", "quantity": 1, "unit_price": 200.0},
            {"item_name": "Knee X-Ray Imaging", "quantity": 1, "unit_price": 150.0}
        ]
    })
    assert bill_res.status_code == 201
    bill_id = bill_res.json()["data"]["bill_id"]
    assert bill_res.json()["data"]["total_amount"] == 350.0
    assert bill_res.json()["data"]["net_amount"] == 340.0

    # 8. Complete Appointment & Settle Bill
    client.put(f"/api/v1/appointments/{apt_id}", json={"status": "completed"})
    client.patch(f"/api/v1/billing/{bill_id}", json={"payment_status": "paid"})

    # 9. Verify Patient Medical History & Billing Records
    hist_rec = client.get(f"/api/v1/medical-records/patient/{patient_id}")
    assert hist_rec.status_code == 200
    assert len(hist_rec.json()["data"]) == 1

    hist_rx = client.get(f"/api/v1/prescriptions/patient/{patient_id}")
    assert hist_rx.status_code == 200
    assert len(hist_rx.json()["data"]) == 1

    hist_bill = client.get(f"/api/v1/billing/patient/{patient_id}")
    assert hist_bill.status_code == 200
    assert hist_bill.json()["data"][0]["payment_status"] == "paid"

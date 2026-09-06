import pytest


def test_full_phase3_4_5_6_integration(client, admin_headers):
    # Phase 3: Auth Login
    auth_res = client.post("/api/v1/auth/login", json={
        "username_or_email": "admin_test",
        "password": "admin123"
    })
    assert auth_res.status_code == 200
    assert auth_res.json()["success"] is True
    assert "access_token" in auth_res.json()["data"]

    # Phase 4: Patient Management
    patient_res = client.post("/api/v1/patients/", headers=admin_headers, json={
        "name": "Sarah Connor",
        "age": 35,
        "gender": "Female",
        "is_active": True
    })
    assert patient_res.status_code == 201
    patient_id = patient_res.json()["data"]["id"]

    patient_get = client.get(f"/api/v1/patients/{patient_id}", headers=admin_headers)
    assert patient_get.status_code == 200
    assert patient_get.json()["data"]["name"] == "Sarah Connor"

    # Phase 5: Doctor Management
    doctor_res = client.post("/api/v1/doctors/", headers=admin_headers, json={
        "name": "Dr. Gregory House",
        "specialization": "Diagnostic Medicine",
        "is_active": True,
        "is_available": True
    })
    assert doctor_res.status_code == 201
    doctor_id = doctor_res.json()["data"]["id"]

    doctor_get = client.get(f"/api/v1/doctors/{doctor_id}", headers=admin_headers)
    assert doctor_get.status_code == 200
    assert doctor_get.json()["data"]["name"] == "Dr. Gregory House"

    # Phase 6: Appointment Management Flow
    # 1. Create Appointment
    apt_res = client.post("/api/v1/appointments/", headers=admin_headers, json={
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "appointment_date": "2026-10-01",
        "appointment_time": "09:30:00",
        "reason": "Unexplained symptoms consultation",
        "notes": "Patient referred by clinic"
    })
    assert apt_res.status_code == 201
    apt_data = apt_res.json()["data"]
    apt_id = apt_data["apt_id"]
    assert apt_id == "APT-000001"
    assert apt_data["status"] == "scheduled"
    assert apt_data["patient"]["name"] == "Sarah Connor"
    assert apt_data["doctor"]["name"] == "Dr. Gregory House"

    # 2. Confirm Appointment
    confirm_res = client.put(f"/api/v1/appointments/{apt_id}", headers=admin_headers, json={
        "status": "confirmed",
        "notes": "Confirmed appointment with patient"
    })
    assert confirm_res.status_code == 200
    assert confirm_res.json()["data"]["status"] == "confirmed"

    # 3. Reschedule Appointment
    resched_res = client.patch(f"/api/v1/appointments/{apt_id}/reschedule", headers=admin_headers, json={
        "appointment_date": "2026-10-02",
        "appointment_time": "11:00:00"
    })
    assert resched_res.status_code == 200
    assert resched_res.json()["data"]["appointment_date"] == "2026-10-02"

    # 4. Complete Appointment
    complete_res = client.put(f"/api/v1/appointments/{apt_id}", headers=admin_headers, json={
        "status": "completed"
    })
    assert complete_res.status_code == 200
    assert complete_res.json()["data"]["status"] == "completed"

    # 5. Verify in Appointments List
    list_res = client.get(f"/api/v1/appointments/?patient_id={patient_id}", headers=admin_headers)
    assert list_res.status_code == 200
    assert list_res.json()["data"]["total"] == 1

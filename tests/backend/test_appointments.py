import pytest
from datetime import date, time
from app.models.appointment import Appointment
from app.utils.id_generator import generate_appointment_id
from tests.backend.conftest import SessionLocal


def test_appointment_id_generator():
    db = SessionLocal()
    id1 = generate_appointment_id(db)
    assert id1 == "APT-000001"

    apt = Appointment(
        apt_id=id1,
        patient_id=1,
        doctor_id=1,
        appointment_date=date(2026, 9, 10),
        appointment_time=time(10, 0),
        status="scheduled",
    )
    db.add(apt)
    db.commit()

    id2 = generate_appointment_id(db)
    assert id2 == "APT-000002"
    db.close()


def test_create_appointment_success(client):
    # Create patient & doctor
    res_p = client.post("/api/v1/patients/", json={"name": "John Doe", "age": 30, "gender": "Male", "is_active": True})
    assert res_p.status_code == 201
    patient_id = res_p.json()["data"]["id"]

    res_d = client.post("/api/v1/doctors/", json={"name": "Dr. Smith", "specialization": "Cardiology", "is_active": True, "is_available": True})
    assert res_d.status_code == 201
    doctor_id = res_d.json()["data"]["id"]

    # Create appointment
    payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "appointment_date": "2026-09-10",
        "appointment_time": "10:00:00",
        "reason": "General consultation",
        "notes": "First visit"
    }
    res_apt = client.post("/api/v1/appointments/", json=payload)
    assert res_apt.status_code == 201
    data = res_apt.json()["data"]
    assert data["apt_id"] == "APT-000001"
    assert data["status"] == "scheduled"
    assert data["patient"]["id"] == patient_id
    assert data["doctor"]["id"] == doctor_id


def test_create_appointment_invalid_and_inactive_entities(client):
    res_p = client.post("/api/v1/patients/", json={"name": "Active Patient", "is_active": True})
    active_p_id = res_p.json()["data"]["id"]
    res_in_p = client.post("/api/v1/patients/", json={"name": "Inactive Patient", "is_active": False})
    inactive_p_id = res_in_p.json()["data"]["id"]

    res_d = client.post("/api/v1/doctors/", json={"name": "Active Doctor", "is_active": True, "is_available": True})
    active_d_id = res_d.json()["data"]["id"]
    res_in_d = client.post("/api/v1/doctors/", json={"name": "Inactive Doctor", "is_active": False, "is_available": True})
    inactive_d_id = res_in_d.json()["data"]["id"]
    res_un_d = client.post("/api/v1/doctors/", json={"name": "Unavailable Doctor", "is_active": True, "is_available": False})
    unavail_d_id = res_un_d.json()["data"]["id"]

    # 1. Invalid Patient ID
    res = client.post("/api/v1/appointments/", json={"patient_id": 999, "doctor_id": active_d_id, "appointment_date": "2026-09-10", "appointment_time": "10:00:00"})
    assert res.status_code == 404

    # 2. Inactive Patient
    res = client.post("/api/v1/appointments/", json={"patient_id": inactive_p_id, "doctor_id": active_d_id, "appointment_date": "2026-09-10", "appointment_time": "10:00:00"})
    assert res.status_code == 400

    # 3. Invalid Doctor ID
    res = client.post("/api/v1/appointments/", json={"patient_id": active_p_id, "doctor_id": 999, "appointment_date": "2026-09-10", "appointment_time": "10:00:00"})
    assert res.status_code == 404

    # 4. Inactive Doctor
    res = client.post("/api/v1/appointments/", json={"patient_id": active_p_id, "doctor_id": inactive_d_id, "appointment_date": "2026-09-10", "appointment_time": "10:00:00"})
    assert res.status_code == 400

    # 5. Unavailable Doctor
    res = client.post("/api/v1/appointments/", json={"patient_id": active_p_id, "doctor_id": unavail_d_id, "appointment_date": "2026-09-10", "appointment_time": "10:00:00"})
    assert res.status_code == 400


def test_double_booking_prevention(client):
    res_p1 = client.post("/api/v1/patients/", json={"name": "Patient One"})
    p1_id = res_p1.json()["data"]["id"]
    res_p2 = client.post("/api/v1/patients/", json={"name": "Patient Two"})
    p2_id = res_p2.json()["data"]["id"]

    res_d = client.post("/api/v1/doctors/", json={"name": "Busy Doctor"})
    d_id = res_d.json()["data"]["id"]

    apt_payload = {
        "patient_id": p1_id,
        "doctor_id": d_id,
        "appointment_date": "2026-09-10",
        "appointment_time": "10:00:00"
    }
    # First booking succeeds
    res1 = client.post("/api/v1/appointments/", json=apt_payload)
    assert res1.status_code == 201

    # Second booking at same date/time fails (Double booking conflict)
    apt_payload2 = {
        "patient_id": p2_id,
        "doctor_id": d_id,
        "appointment_date": "2026-09-10",
        "appointment_time": "10:00:00"
    }
    res2 = client.post("/api/v1/appointments/", json=apt_payload2)
    assert res2.status_code in (400, 409)
    assert "already has an active appointment" in res2.json()["message"]


def test_list_appointments_and_filtering(client):
    res_p = client.post("/api/v1/patients/", json={"name": "Patient A"})
    p_id = res_p.json()["data"]["id"]
    res_d = client.post("/api/v1/doctors/", json={"name": "Doctor B"})
    d_id = res_d.json()["data"]["id"]

    client.post("/api/v1/appointments/", json={"patient_id": p_id, "doctor_id": d_id, "appointment_date": "2026-09-10", "appointment_time": "10:00:00"})
    client.post("/api/v1/appointments/", json={"patient_id": p_id, "doctor_id": d_id, "appointment_date": "2026-09-11", "appointment_time": "11:00:00"})

    # List all
    res = client.get("/api/v1/appointments/")
    assert res.status_code == 200
    assert res.json()["data"]["total"] == 2

    # Filter by date
    res_filtered = client.get("/api/v1/appointments/?appointment_date=2026-09-10")
    assert res_filtered.status_code == 200
    assert res_filtered.json()["data"]["total"] == 1


def test_get_update_reschedule_cancel_workflow(client):
    res_p = client.post("/api/v1/patients/", json={"name": "Patient Workflow"})
    p_id = res_p.json()["data"]["id"]
    res_d = client.post("/api/v1/doctors/", json={"name": "Doctor Workflow"})
    d_id = res_d.json()["data"]["id"]

    res_create = client.post("/api/v1/appointments/", json={
        "patient_id": p_id,
        "doctor_id": d_id,
        "appointment_date": "2026-09-10",
        "appointment_time": "10:00:00",
        "reason": "Checkup"
    })
    apt_id_str = res_create.json()["data"]["apt_id"]
    numeric_id = res_create.json()["data"]["id"]

    # Get details by APT ID
    res_get = client.get(f"/api/v1/appointments/{apt_id_str}")
    assert res_get.status_code == 200
    assert res_get.json()["data"]["id"] == numeric_id

    # Update appointment status to confirmed
    res_up = client.put(f"/api/v1/appointments/{apt_id_str}", json={"status": "confirmed", "notes": "Patient confirmed via SMS"})
    assert res_up.status_code == 200
    assert res_up.json()["data"]["status"] == "confirmed"

    # Reschedule appointment (2026-09-11 is Friday - a valid working weekday)
    res_resched = client.patch(f"/api/v1/appointments/{apt_id_str}/reschedule", json={"appointment_date": "2026-09-11", "appointment_time": "14:00:00"})
    assert res_resched.status_code == 200
    assert res_resched.json()["data"]["appointment_date"] == "2026-09-11"
    assert res_resched.json()["data"]["appointment_time"] == "14:00:00"

    # Cancel appointment
    res_cancel = client.delete(f"/api/v1/appointments/{apt_id_str}")
    assert res_cancel.status_code == 200
    assert res_cancel.json()["data"]["status"] == "cancelled"


def test_status_transition_rules(client):
    res_p = client.post("/api/v1/patients/", json={"name": "Patient State"})
    p_id = res_p.json()["data"]["id"]
    res_d = client.post("/api/v1/doctors/", json={"name": "Doctor State"})
    d_id = res_d.json()["data"]["id"]

    res_create = client.post("/api/v1/appointments/", json={
        "patient_id": p_id,
        "doctor_id": d_id,
        "appointment_date": "2026-09-15",
        "appointment_time": "09:00:00"
    })
    apt_id_str = res_create.json()["data"]["apt_id"]

    # Invalid transition: scheduled -> completed (must go to confirmed first)
    res_inv = client.put(f"/api/v1/appointments/{apt_id_str}", json={"status": "completed"})
    assert res_inv.status_code == 400

    # Valid: scheduled -> confirmed
    client.put(f"/api/v1/appointments/{apt_id_str}", json={"status": "confirmed"})

    # Valid: confirmed -> completed
    res_comp = client.put(f"/api/v1/appointments/{apt_id_str}", json={"status": "completed"})
    assert res_comp.status_code == 200
    assert res_comp.json()["data"]["status"] == "completed"

    # Invalid: completed -> scheduled
    res_reopen = client.put(f"/api/v1/appointments/{apt_id_str}", json={"status": "scheduled"})
    assert res_reopen.status_code == 400

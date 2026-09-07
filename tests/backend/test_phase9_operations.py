from datetime import date, timedelta
from app.models.user import User
from app.models.department import Department
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.core.security import hash_password, create_access_token


def create_test_user(db_session, username, role, patient_id=None, doctor_id=None):
    pwd_hash = hash_password("password123")
    user = User(
        username=username,
        email=f"{username}@hospital.org",
        password_hash=pwd_hash,
        role=role,
        is_active=True,
        patient_id=patient_id,
        doctor_id=doctor_id,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token({"sub": str(user.id), "role": role})
    return user, token


def test_phase9_complete_hospital_operations_workflow(client, db_session):
    # 1. Setup Department, Doctor, Patient, and Users
    dept = Department(name="Cardiology", description="Cardiology Dept")
    db_session.add(dept)
    db_session.commit()
    db_session.refresh(dept)

    doc = Doctor(
        name="Dr. Sarah Connor",
        specialization="Cardiology",
        department_id=dept.id,
        phone="9876543210",
        is_available=True
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)

    pat = Patient(
        name="John Doe",
        age=38,
        gender="Male",
        phone="9123456789"
    )
    db_session.add(pat)
    db_session.commit()
    db_session.refresh(pat)

    admin_user, admin_token = create_test_user(db_session, "admin_phase9", "ADMIN")
    doc_user, doc_token = create_test_user(db_session, "doc_phase9", "DOCTOR", doctor_id=doc.id)
    lab_user, lab_token = create_test_user(db_session, "lab_phase9", "LABORATORY")
    pharm_user, pharm_token = create_test_user(db_session, "pharm_phase9", "PHARMACY")
    dept_head_user, dept_head_token = create_test_user(db_session, "dept_head_phase9", "DEPARTMENT_HEAD")
    rec_user, rec_token = create_test_user(db_session, "rec_phase9", "RECEPTIONIST")

    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    doc_headers = {"Authorization": f"Bearer {doc_token}"}
    lab_headers = {"Authorization": f"Bearer {lab_token}"}
    pharm_headers = {"Authorization": f"Bearer {pharm_token}"}
    rec_headers = {"Authorization": f"Bearer {rec_token}"}
    dept_head_headers = {"Authorization": f"Bearer {dept_head_token}"}

    # ----------------------------------------------------
    # 2. Appointment Workflow (OP/IP Handling & Doctor Availability)
    # ----------------------------------------------------
    apt_data = {
        "patient_id": pat.id,
        "doctor_id": doc.id,
        "appointment_date": str(date.today() + timedelta(days=1)),
        "appointment_time": "10:00:00",
        "reason": "Chest Pain & Routine Checkup",
        "appointment_type": "OP"
    }
    apt_res = client.post("/api/v1/appointments/", json=apt_data, headers=admin_headers)
    assert apt_res.status_code == 201, apt_res.json()
    apt_json = apt_res.json()["data"]
    apt_id = apt_json["id"]
    assert apt_json["appointment_type"] == "OP"

    # Reschedule appointment
    reschedule_data = {
        "appointment_date": str(date.today() + timedelta(days=2)),
        "appointment_time": "11:00:00"
    }
    resc_res = client.patch(f"/api/v1/appointments/{apt_id}/reschedule", json=reschedule_data, headers=admin_headers)
    assert resc_res.status_code == 200, resc_res.json()

    # ----------------------------------------------------
    # 3. Laboratory Management Workflow
    # ----------------------------------------------------
    # Create Lab Catalog item
    cat_data = {
        "test_code": "ECG-001",
        "test_name": "Electrocardiogram 12-Lead",
        "department_id": dept.id,
        "description": "Standard ECG scan",
        "cost": 1200.0,
        "reference_range": "Normal Sinus Rhythm",
        "sample_type": "None / Direct Scan"
    }
    cat_res = client.post("/api/v1/laboratory/catalog", json=cat_data, headers=lab_headers)
    assert cat_res.status_code == 201, cat_res.json()
    cat_id = cat_res.json()["id"]

    # Order Lab Test (Doctor/Admin)
    order_data = {
        "patient_id": pat.id,
        "doctor_id": doc.id,
        "lab_test_id": cat_id,
        "appointment_id": apt_id,
        "priority": "URGENT",
        "doctor_notes": "Evaluate ECG for arrhythmia"
    }
    order_res = client.post("/api/v1/laboratory/orders", json=order_data, headers=doc_headers)
    assert order_res.status_code == 201, order_res.json()
    order_id = order_res.json()["id"]

    # Collect sample
    sample_data = {"sample_id": "SMP-ECG-99", "sample_type": "Direct Scan"}
    sample_res = client.post(f"/api/v1/laboratory/orders/{order_id}/collect-sample", json=sample_data, headers=lab_headers)
    assert sample_res.status_code == 200, sample_res.json()
    assert sample_res.json()["status"] == "SAMPLE_COLLECTED"

    # Enter Result (Lab Tech)
    result_data = {
        "result_value": "Sinus Tachycardia detected at 110 bpm",
        "reference_range": "60-100 bpm",
        "is_abnormal": True,
        "technician_notes": "Patient was slightly anxious during procedure"
    }
    result_res = client.post(f"/api/v1/laboratory/orders/{order_id}/results", json=result_data, headers=lab_headers)
    assert result_res.status_code == 201, result_res.json()
    result_id = result_res.json()["id"]
    assert result_res.json()["is_abnormal"] is True

    # Review Result (Doctor)
    review_data = {"doctor_notes": "Prescribe beta-blockers and schedule follow-up"}
    review_res = client.post(f"/api/v1/laboratory/results/{result_id}/review", json=review_data, headers=doc_headers)
    assert review_res.status_code == 200, review_res.json()
    assert review_res.json()["doctor_review_status"] == "REVIEWED"

    # Patient Lab Report
    report_res = client.get(f"/api/v1/laboratory/patients/{pat.id}/report", headers=doc_headers)
    assert report_res.status_code == 200
    assert report_res.json()["total_orders"] == 1
    assert report_res.json()["completed_orders"] == 1

    # ----------------------------------------------------
    # 4. Pharmacy Management Workflow
    # ----------------------------------------------------
    # Add Medicine to Inventory
    med_data = {
        "medicine_code": "MED-ATEN-50",
        "name": "Atenolol 50mg",
        "category": "Beta Blocker",
        "unit_price": 15.0,
        "stock_quantity": 100,
        "reorder_level": 20,
        "expiry_date": str(date.today() + timedelta(days=365)),
        "manufacturer": "PharmaCorp",
        "location_rack": "Rack-B-12"
    }
    med_res = client.post("/api/v1/pharmacy/inventory", json=med_data, headers=pharm_headers)
    assert med_res.status_code == 201, med_res.json()
    med_id = med_res.json()["id"]

    # Dispense Medicines & Auto-Deduct Inventory
    dispense_data = {
        "patient_id": pat.id,
        "notes": "Post ECG review dispensation",
        "items": [
            {"medicine_id": med_id, "quantity": 10}
        ]
    }
    dispense_res = client.post("/api/v1/pharmacy/dispense", json=dispense_data, headers=pharm_headers)
    assert dispense_res.status_code == 201, dispense_res.json()
    dispense_json = dispense_res.json()
    assert dispense_json["total_amount"] == 150.0  # 10 * 15.0

    # Verify inventory reduced from 100 to 90
    inv_check = client.get(f"/api/v1/pharmacy/inventory/{med_id}", headers=pharm_headers)
    assert inv_check.status_code == 200
    assert inv_check.json()["stock_quantity"] == 90

    # ----------------------------------------------------
    # 5. IP / Admission Management Workflow
    # ----------------------------------------------------
    # Create Ward & Beds
    ward_data = {
        "ward_name": "Cardiac Care Unit (CCU)",
        "ward_type": "ICU",
        "department_id": dept.id,
        "total_beds": 0
    }
    ward_res = client.post("/api/v1/admissions/wards", json=ward_data, headers=admin_headers)
    assert ward_res.status_code == 201, ward_res.json()
    ward_id = ward_res.json()["id"]

    bed1_data = {"ward_id": ward_id, "bed_number": "CCU-101", "bed_type": "ICU", "daily_rate": 2500.0}
    bed1_res = client.post("/api/v1/admissions/beds", json=bed1_data, headers=admin_headers)
    assert bed1_res.status_code == 201
    bed1_id = bed1_res.json()["id"]

    bed2_data = {"ward_id": ward_id, "bed_number": "CCU-102", "bed_type": "ICU", "daily_rate": 2500.0}
    bed2_res = client.post("/api/v1/admissions/beds", json=bed2_data, headers=admin_headers)
    assert bed2_res.status_code == 201
    bed2_id = bed2_res.json()["id"]

    # Admit Patient
    admit_data = {
        "patient_id": pat.id,
        "doctor_id": doc.id,
        "department_id": dept.id,
        "bed_id": bed1_id,
        "admission_type": "EMERGENCY",
        "reason_for_admission": "Severe angina monitoring"
    }
    admit_res = client.post("/api/v1/admissions", json=admit_data, headers=rec_headers)
    assert admit_res.status_code == 201, admit_res.json()
    adm_id = admit_res.json()["id"]

    # Transfer patient to Bed 2
    transfer_data = {"to_bed_id": bed2_id, "reason": "Patient requested room shift"}
    transfer_res = client.post(f"/api/v1/admissions/{adm_id}/transfer", json=transfer_data, headers=rec_headers)
    assert transfer_res.status_code == 200, transfer_res.json()
    assert transfer_res.json()["bed_id"] == bed2_id

    # Discharge patient
    discharge_data = {"discharge_summary": "Patient stabilized. Discharged with oral medications."}
    discharge_res = client.post(f"/api/v1/admissions/{adm_id}/discharge", json=discharge_data, headers=doc_headers)
    assert discharge_res.status_code == 200, discharge_res.json()
    assert discharge_res.json()["status"] == "DISCHARGED"

    # ----------------------------------------------------
    # 6. Billing & Payments Workflow
    # ----------------------------------------------------
    # Create Comprehensive Bill
    bill_data = {
        "patient_id": pat.id,
        "appointment_id": apt_id,
        "admission_id": adm_id,
        "lab_order_id": order_id,
        "pharmacy_dispense_id": dispense_json["id"],
        "billing_type": "COMPREHENSIVE",
        "discount": 50.0,
        "tax": 100.0,
        "payment_method": "upi",
        "notes": "Full discharge billing",
        "items": [
            {"item_name": "Consultation Fee", "quantity": 1, "unit_price": 500.0},
            {"item_name": "ECG Scan (Lab)", "quantity": 1, "unit_price": 1200.0},
            {"item_name": "Pharmacy Medicines", "quantity": 1, "unit_price": 150.0},
            {"item_name": "ICU Room Charges (1 Day)", "quantity": 1, "unit_price": 2500.0}
        ]
    }
    # Total items = 500 + 1200 + 150 + 2500 = 4350. Net = 4350 - 50 + 100 = 4400.
    bill_res = client.post("/api/v1/billing/", json=bill_data, headers=rec_headers)
    assert bill_res.status_code == 201, bill_res.json()
    bill_json = bill_res.json()["data"]
    bill_id = bill_json["bill_id"]
    assert bill_json["net_amount"] == 4400.0

    # Record Payment Transaction
    pay_data = {"amount": 4400.0, "payment_method": "upi", "notes": "Paid via Google Pay"}
    pay_res = client.post(f"/api/v1/billing/{bill_id}/payments", json=pay_data, headers=rec_headers)
    assert pay_res.status_code == 201, pay_res.json()

    # Verify Bill Status updated to 'paid'
    bill_verify = client.get(f"/api/v1/billing/{bill_id}", headers=rec_headers)
    assert bill_verify.status_code == 200
    assert bill_verify.json()["data"]["payment_status"] == "paid"

    # Process Partial Refund
    refund_data = {"amount": 200.0, "reason": "Overcharge discount adjustment"}
    refund_res = client.post(f"/api/v1/billing/{bill_id}/refund", json=refund_data, headers=rec_headers)
    assert refund_res.status_code == 200, refund_res.json()
    assert refund_res.json()["data"]["transaction_type"] == "REFUND"

    # ----------------------------------------------------
    # 7. Department Head Dashboard
    # ----------------------------------------------------
    dept_head_res = client.get(f"/api/v1/department-head/overview/{dept.id}", headers=dept_head_headers)
    assert dept_head_res.status_code == 200, dept_head_res.json()
    overview = dept_head_res.json()
    assert overview["stats"]["department_id"] == dept.id
    assert overview["stats"]["doctors_count"] == 1
    assert overview["stats"]["patients_count"] == 1
    assert len(overview["doctors"]) == 1
    assert overview["doctors"][0]["name"] == "Dr. Sarah Connor"

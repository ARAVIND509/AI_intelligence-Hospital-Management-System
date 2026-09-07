from datetime import date, time, timedelta
from app.models.user import User
from app.models.department import Department
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.billing import Billing
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


def test_phase10_ai_analytics_workflow(client, db_session):
    # 1. Setup Data
    dept = Department(name="Neurology", description="Neurology Dept")
    db_session.add(dept)
    db_session.commit()
    db_session.refresh(dept)

    doc = Doctor(name="Dr. Alan Turing", specialization="Neurology", department_id=dept.id, is_available=True)
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)

    pat = Patient(name="Ada Lovelace", age=36, gender="Female", phone="9988776655", medical_history="Migraine history")
    db_session.add(pat)
    db_session.commit()
    db_session.refresh(pat)

    apt = Appointment(apt_id="APT-1001", patient_id=pat.id, doctor_id=doc.id, appointment_date=date.today(), appointment_time=time(10, 0), status="completed")
    db_session.add(apt)

    bill = Billing(bill_id="BILL-1001", patient_id=pat.id, appointment_id=apt.id, total_amount=1500.0, net_amount=1500.0, payment_status="paid")
    db_session.add(bill)
    db_session.commit()

    admin_user, admin_token = create_test_user(db_session, "admin_phase10", "ADMIN")
    doc_user, doc_token = create_test_user(db_session, "doc_phase10", "DOCTOR", doctor_id=doc.id)
    dept_head_user, dept_head_token = create_test_user(db_session, "dept_head_phase10", "DEPARTMENT_HEAD")

    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    doc_headers = {"Authorization": f"Bearer {doc_token}"}
    dept_head_headers = {"Authorization": f"Bearer {dept_head_token}"}

    # ----------------------------------------------------
    # 2. Hospital Analytics Dashboard & Workload Endpoints
    # ----------------------------------------------------
    dash_res = client.get("/api/v1/analytics/dashboard", headers=admin_headers)
    assert dash_res.status_code == 200, dash_res.json()
    dash = dash_res.json()
    assert dash["total_patients"] >= 1
    assert dash["total_revenue"] >= 1500.0

    workload_res = client.get("/api/v1/analytics/doctor-workload", headers=dept_head_headers)
    assert workload_res.status_code == 200, workload_res.json()
    assert len(workload_res.json()) >= 1

    perf_res = client.get("/api/v1/analytics/department-performance", headers=admin_headers)
    assert perf_res.status_code == 200, perf_res.json()

    # ----------------------------------------------------
    # 3. Patient Analytics
    # ----------------------------------------------------
    pat_res = client.get(f"/api/v1/analytics/patients/{pat.id}", headers=doc_headers)
    assert pat_res.status_code == 200, pat_res.json()
    pat_analytics = pat_res.json()
    assert pat_analytics["patient_name"] == "Ada Lovelace"
    assert len(pat_analytics["timeline"]) >= 1

    # ----------------------------------------------------
    # 4. AI-Based Features (Summary & Lab Explanation)
    # ----------------------------------------------------
    ai_summary_res = client.post(f"/api/v1/ai/patient-summary/{pat.id}", json={"patient_id": pat.id}, headers=doc_headers)
    assert ai_summary_res.status_code == 200, ai_summary_res.json()
    summary = ai_summary_res.json()
    assert "Migraine history" in summary["previous_conditions"]
    assert "ai_disclaimer" in summary

    lab_explain_res = client.post("/api/v1/ai/explain-lab-result", json={
        "test_name": "Hemoglobin",
        "result_value": "10.2 g/dL",
        "reference_range": "12.0 - 15.5 g/dL",
        "is_abnormal": True
    }, headers=doc_headers)
    assert lab_explain_res.status_code == 200, lab_explain_res.json()
    explanation = lab_explain_res.json()
    assert "anemia" in explanation["explanation"].lower() or "below" in explanation["explanation"].lower()

    # ----------------------------------------------------
    # 5. Predictive Analytics
    # ----------------------------------------------------
    noshow_res = client.post("/api/v1/ai/predict/no-show", json={
        "patient_id": pat.id,
        "doctor_id": doc.id,
        "appointment_date": str(date.today() + timedelta(days=10)),
        "appointment_time": "14:00:00"
    }, headers=doc_headers)
    assert noshow_res.status_code == 200, noshow_res.json()
    assert "no_show_risk_score" in noshow_res.json()

    readm_res = client.post("/api/v1/ai/predict/readmission-risk", json={
        "patient_id": pat.id,
        "length_of_stay_days": 8,
        "admission_type": "EMERGENCY"
    }, headers=doc_headers)
    assert readm_res.status_code == 200, readm_res.json()
    assert readm_res.json()["risk_category"] in ["LOW", "MEDIUM", "HIGH"]

    bed_fc = client.get("/api/v1/ai/predict/bed-occupancy", headers=dept_head_headers)
    assert bed_fc.status_code == 200, bed_fc.json()

    med_fc = client.get("/api/v1/ai/predict/medicine-demand", headers=admin_headers)
    assert med_fc.status_code == 200, med_fc.json()

    lab_fc = client.get("/api/v1/ai/predict/lab-workload", headers=admin_headers)
    assert lab_fc.status_code == 200, lab_fc.json()

    # ----------------------------------------------------
    # 6. Hospital Reports Generator
    # ----------------------------------------------------
    daily_rep = client.get("/api/v1/reports/daily", headers=admin_headers)
    assert daily_rep.status_code == 200, daily_rep.json()

    monthly_rep = client.get("/api/v1/reports/monthly", headers=admin_headers)
    assert monthly_rep.status_code == 200, monthly_rep.json()

    dept_rep = client.get(f"/api/v1/reports/department/{dept.id}", headers=dept_head_headers)
    assert dept_rep.status_code == 200, dept_rep.json()

    rev_rep = client.get("/api/v1/reports/revenue", headers=admin_headers)
    assert rev_rep.status_code == 200, rev_rep.json()

    pharm_rep = client.get("/api/v1/reports/pharmacy", headers=admin_headers)
    assert pharm_rep.status_code == 200, pharm_rep.json()

    lab_rep = client.get("/api/v1/reports/laboratory", headers=admin_headers)
    assert lab_rep.status_code == 200, lab_rep.json()

    stats_rep = client.get("/api/v1/reports/patient-statistics", headers=admin_headers)
    assert stats_rep.status_code == 200, stats_rep.json()

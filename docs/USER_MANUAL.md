# MediMind AI — End-User Staff Manual

This guide outlines daily workflows for hospital staff roles using **MediMind AI**.

---

## 🏥 Complete Hospital Workflow Overview

```text
[Receptionist] Registration & Appointment Booking (OP/IP)
        ↓
[Doctor] Patient Consultation, Diagnosis & Lab/Pharmacy Orders
        ↓
[Laboratory] Sample Collection & Test Result Entry
        ↓
[Pharmacy] Prescription Processing & Dispensing
        ↓
[Receptionist] Billing, Payments & Patient Discharge
```

---

## 📋 Role-Based Guides

### 1. Receptionist Workflow
1. **Patient Registration**: Register new patients (`POST /api/v1/patients/`).
2. **Book Appointment**: Select doctor, date, and appointment type (`OP` outpatient or `IP` inpatient).
3. **Inpatient Admission**: Assign available bed in General Ward / ICU.
4. **Billing & Invoice**: Process consultation, lab, pharmacy, and admission charges; record payment via cash/card/UPI.

### 2. Doctor Workflow
1. **Consultation**: View patient medical history timeline and previous lab results.
2. **Order Lab Tests**: Select required tests from catalog and set priority (`NORMAL`, `URGENT`, `EMERGENCY`).
3. **Prescribe Medications**: Add prescription medicines with dosage and duration.
4. **Review Lab Results**: Inspect technician entries and record doctor sign-off notes.
5. **AI Clinical Assistance**: Request AI Health Summary or AI Lab Report Explanations for decision support.
6. **Discharge Summary**: Record discharge notes when patient is ready for release.

### 3. Laboratory Staff Workflow
1. **View Lab Orders**: Check incoming doctor test orders.
2. **Collect Sample**: Assign sample ID/barcode and record collection time.
3. **Enter Results**: Record result values, reference ranges, and flag abnormal parameters.

### 4. Pharmacy Staff Workflow
1. **Inventory Management**: Add medicines, set unit prices, and monitor low-stock alerts.
2. **Dispense Prescription**: Select prescription, verify stock availability, and process dispensation (inventory auto-deducts).

### 5. Department Head Workflow
1. **Department Dashboard**: Monitor total patients, doctor workloads, appointment trends, and bed occupancy rates.
2. **Performance Metrics**: View department utilization and generate monthly performance reports.

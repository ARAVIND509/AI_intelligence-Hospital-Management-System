import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.admission import Ward, Bed, Admission, BedTransferLog
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.department import Department
from app.repositories.admission_repository import (
    ward_repository,
    bed_repository,
    admission_repository,
    bed_transfer_log_repository,
)
from app.schemas.admission import (
    WardCreate,
    BedCreate,
    AdmissionCreate,
    BedTransferRequest,
    DischargeRequest,
)


class AdmissionService:
    def create_ward(self, db: Session, obj_in: WardCreate) -> Ward:
        existing = ward_repository.get_by_name(db, obj_in.ward_name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ward '{obj_in.ward_name}' already exists"
            )
        return ward_repository.create(db, obj_in=obj_in)

    def list_wards(self, db: Session) -> List[Ward]:
        wards, _ = ward_repository.get_multi(db, limit=100)
        return wards

    def create_bed(self, db: Session, obj_in: BedCreate) -> Bed:
        ward = ward_repository.get(db, obj_in.ward_id)
        if not ward:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ward not found")

        bed = bed_repository.create(db, obj_in=obj_in)
        # Update total beds in ward
        ward.total_beds += 1
        db.add(ward)
        db.commit()
        db.refresh(bed)
        return bed

    def list_beds(self, db: Session, ward_id: Optional[int] = None, status_filter: Optional[str] = None) -> List[Bed]:
        filters = {}
        if ward_id:
            filters["ward_id"] = ward_id
        if status_filter:
            filters["status"] = status_filter
        beds, _ = bed_repository.get_multi(db, limit=200, filters=filters)
        return beds

    def admit_patient(self, db: Session, obj_in: AdmissionCreate) -> Admission:
        patient = db.query(Patient).filter(Patient.id == obj_in.patient_id).first()
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
        doctor = db.query(Doctor).filter(Doctor.id == obj_in.doctor_id).first()
        if not doctor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
        department = db.query(Department).filter(Department.id == obj_in.department_id).first()
        if not department:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

        bed = bed_repository.get(db, obj_in.bed_id)
        if not bed:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bed not found")
        if bed.status != "VACANT":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Bed #{bed.bed_number} is not vacant (Current status: {bed.status})")

        # Check if patient already has active admission
        active_adm = db.query(Admission).filter(Admission.patient_id == obj_in.patient_id, Admission.status == "ADMITTED").first()
        if active_adm:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Patient already has an active admission")

        admission_number = f"ADM-{uuid.uuid4().hex[:8].upper()}"
        adm_data = obj_in.model_dump()
        adm_data["admission_number"] = admission_number
        adm_data["status"] = "ADMITTED"
        adm_data["admission_date"] = datetime.now(timezone.utc)

        admission = admission_repository.create(db, obj_in=adm_data)

        # Mark bed as occupied
        bed.status = "OCCUPIED"
        db.add(bed)
        db.commit()

        db.refresh(admission)
        return admission

    def get_admission(self, db: Session, admission_id: int) -> Admission:
        admission = admission_repository.get(db, admission_id)
        if not admission:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admission record not found")
        return admission

    def list_admissions(
        self, db: Session, skip: int = 0, limit: int = 50, patient_id: Optional[int] = None, status_filter: Optional[str] = None
    ) -> tuple[List[Admission], int]:
        filters = {}
        if patient_id:
            filters["patient_id"] = patient_id
        if status_filter:
            filters["status"] = status_filter
        return admission_repository.get_multi(db, skip=skip, limit=limit, filters=filters)

    def transfer_bed(self, db: Session, admission_id: int, user_id: int, transfer_req: BedTransferRequest) -> Admission:
        admission = self.get_admission(db, admission_id)
        if admission.status != "ADMITTED":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot transfer patient with admission status '{admission.status}'")

        new_bed = bed_repository.get(db, transfer_req.to_bed_id)
        if not new_bed:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target bed not found")
        if new_bed.status != "VACANT":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Target bed #{new_bed.bed_number} is not vacant")

        old_bed = admission.bed

        # Record transfer log
        log = BedTransferLog(
            admission_id=admission.id,
            from_bed_id=old_bed.id,
            to_bed_id=new_bed.id,
            transfer_date=datetime.now(timezone.utc),
            reason=transfer_req.reason,
            transferred_by_id=user_id,
        )
        db.add(log)

        # Update bed statuses
        old_bed.status = "VACANT"
        new_bed.status = "OCCUPIED"
        db.add(old_bed)
        db.add(new_bed)

        # Update admission target bed
        admission.bed_id = new_bed.id
        db.add(admission)

        db.commit()
        db.refresh(admission)
        return admission

    def discharge_patient(self, db: Session, admission_id: int, discharge_req: DischargeRequest) -> Admission:
        admission = self.get_admission(db, admission_id)
        if admission.status != "ADMITTED":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Patient is already discharged or transferred")

        bed = admission.bed

        admission.status = "DISCHARGED"
        admission.discharge_date = datetime.now(timezone.utc)
        admission.discharge_summary = discharge_req.discharge_summary
        db.add(admission)

        # Release bed
        if bed:
            bed.status = "VACANT"
            db.add(bed)

        db.commit()
        db.refresh(admission)
        return admission


admission_service = AdmissionService()

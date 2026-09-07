import uuid
from datetime import datetime, timezone, date, timedelta
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.pharmacy import MedicineInventory, PharmacyDispense, PharmacyDispenseItem, InventoryLog
from app.models.patient import Patient
from app.models.prescription import Prescription
from app.repositories.pharmacy_repository import (
    medicine_inventory_repository,
    pharmacy_dispense_repository,
    inventory_log_repository,
)
from app.schemas.pharmacy import (
    MedicineInventoryCreate,
    MedicineInventoryUpdate,
    PharmacyDispenseCreate,
)


class PharmacyService:
    def add_medicine(self, db: Session, obj_in: MedicineInventoryCreate) -> MedicineInventory:
        existing = medicine_inventory_repository.get_by_code(db, obj_in.medicine_code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Medicine with code '{obj_in.medicine_code}' already exists"
            )
        return medicine_inventory_repository.create(db, obj_in=obj_in)

    def get_medicine(self, db: Session, medicine_id: int) -> MedicineInventory:
        medicine = medicine_inventory_repository.get(db, medicine_id)
        if not medicine:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicine not found in inventory")
        return medicine

    def list_inventory(self, db: Session, skip: int = 0, limit: int = 50) -> tuple[List[MedicineInventory], int]:
        return medicine_inventory_repository.get_multi(db, skip=skip, limit=limit)

    def update_medicine(self, db: Session, medicine_id: int, obj_in: MedicineInventoryUpdate) -> MedicineInventory:
        medicine = self.get_medicine(db, medicine_id)
        return medicine_inventory_repository.update(db, db_obj=medicine, obj_in=obj_in)

    def get_low_stock_alerts(self, db: Session) -> List[MedicineInventory]:
        return medicine_inventory_repository.get_low_stock(db)

    def get_expiring_soon(self, db: Session, days: int = 30) -> List[MedicineInventory]:
        target_date = date.today() + timedelta(days=days)
        return medicine_inventory_repository.get_expiring_soon(db, target_date)

    def dispense_medicines(self, db: Session, user_id: int, obj_in: PharmacyDispenseCreate) -> PharmacyDispense:
        patient = db.query(Patient).filter(Patient.id == obj_in.patient_id).first()
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

        if obj_in.prescription_id:
            prescription = db.query(Prescription).filter(Prescription.id == obj_in.prescription_id).first()
            if not prescription:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescription not found")

        if not obj_in.items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dispense items list cannot be empty")

        dispense_number = f"DSP-{uuid.uuid4().hex[:8].upper()}"
        total_dispense_amount = 0.0

        dispense = PharmacyDispense(
            dispense_number=dispense_number,
            patient_id=obj_in.patient_id,
            prescription_id=obj_in.prescription_id,
            dispensed_by_id=user_id,
            status="DISPENSED",
            total_amount=0.0,
            notes=obj_in.notes,
        )
        db.add(dispense)
        db.flush()

        for item in obj_in.items:
            medicine = medicine_inventory_repository.get(db, item.medicine_id)
            if not medicine:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Medicine ID {item.medicine_id} not found")

            if medicine.stock_quantity < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for medicine '{medicine.name}'. Available: {medicine.stock_quantity}, Requested: {item.quantity}"
                )

            item_total = medicine.unit_price * item.quantity
            total_dispense_amount += item_total

            # Create dispense item
            dispense_item = PharmacyDispenseItem(
                dispense_id=dispense.id,
                medicine_id=medicine.id,
                medicine_name=medicine.name,
                quantity=item.quantity,
                unit_price=medicine.unit_price,
                total_price=item_total,
            )
            db.add(dispense_item)

            # Deduct inventory & record inventory log
            prev_qty = medicine.stock_quantity
            new_qty = prev_qty - item.quantity
            medicine.stock_quantity = new_qty
            db.add(medicine)

            log = InventoryLog(
                medicine_id=medicine.id,
                change_type="DISPENSED",
                quantity_change=-item.quantity,
                previous_quantity=prev_qty,
                new_quantity=new_qty,
                performed_by_id=user_id,
                notes=f"Dispense #{dispense_number}",
            )
            db.add(log)

        dispense.total_amount = total_dispense_amount
        db.commit()
        db.refresh(dispense)
        return dispense

    def list_dispensed_history(
        self, db: Session, skip: int = 0, limit: int = 50, patient_id: Optional[int] = None
    ) -> tuple[List[PharmacyDispense], int]:
        filters = {}
        if patient_id:
            filters["patient_id"] = patient_id
        return pharmacy_dispense_repository.get_multi(db, skip=skip, limit=limit, filters=filters)


pharmacy_service = PharmacyService()

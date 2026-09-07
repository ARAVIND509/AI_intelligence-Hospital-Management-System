from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from app.repositories.base_repository import CRUDBase
from app.models.pharmacy import MedicineInventory, PharmacyDispense, PharmacyDispenseItem, InventoryLog
from app.schemas.pharmacy import MedicineInventoryCreate, MedicineInventoryUpdate


class CRUDMedicineInventory(CRUDBase[MedicineInventory, MedicineInventoryCreate, MedicineInventoryUpdate]):
    def get_by_code(self, db: Session, medicine_code: str) -> Optional[MedicineInventory]:
        return db.query(MedicineInventory).filter(MedicineInventory.medicine_code == medicine_code).first()

    def get_low_stock(self, db: Session) -> List[MedicineInventory]:
        return db.query(MedicineInventory).filter(MedicineInventory.stock_quantity <= MedicineInventory.reorder_level).all()

    def get_expiring_soon(self, db: Session, target_date: date) -> List[MedicineInventory]:
        return db.query(MedicineInventory).filter(MedicineInventory.expiry_date != None, MedicineInventory.expiry_date <= target_date).all()


class CRUDPharmacyDispense(CRUDBase[PharmacyDispense, dict, dict]):
    def get_by_dispense_number(self, db: Session, dispense_number: str) -> Optional[PharmacyDispense]:
        return db.query(PharmacyDispense).filter(PharmacyDispense.dispense_number == dispense_number).first()

    def get_by_patient(self, db: Session, patient_id: int) -> List[PharmacyDispense]:
        return db.query(PharmacyDispense).filter(PharmacyDispense.patient_id == patient_id).order_by(PharmacyDispense.id.desc()).all()


class CRUDInventoryLog(CRUDBase[InventoryLog, dict, dict]):
    def get_by_medicine(self, db: Session, medicine_id: int) -> List[InventoryLog]:
        return db.query(InventoryLog).filter(InventoryLog.medicine_id == medicine_id).order_by(InventoryLog.id.desc()).all()


medicine_inventory_repository = CRUDMedicineInventory(MedicineInventory)
pharmacy_dispense_repository = CRUDPharmacyDispense(PharmacyDispense)
inventory_log_repository = CRUDInventoryLog(InventoryLog)

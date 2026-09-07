from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User
from app.services.pharmacy_service import pharmacy_service
from app.schemas.pharmacy import (
    MedicineInventoryCreate,
    MedicineInventoryUpdate,
    MedicineInventoryResponse,
    PharmacyDispenseCreate,
    PharmacyDispenseResponse,
)

router = APIRouter(prefix="/pharmacy", tags=["Pharmacy Management"])


@router.post("/inventory", response_model=MedicineInventoryResponse, status_code=status.HTTP_201_CREATED)
def add_medicine_inventory(
    obj_in: MedicineInventoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "PHARMACY"])),
):
    return pharmacy_service.add_medicine(db, obj_in)


@router.get("/inventory", response_model=List[MedicineInventoryResponse])
def list_medicine_inventory(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, _ = pharmacy_service.list_inventory(db, skip=skip, limit=limit)
    return items


@router.get("/inventory/low-stock", response_model=List[MedicineInventoryResponse])
def get_low_stock_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "PHARMACY", "DEPARTMENT_HEAD"])),
):
    return pharmacy_service.get_low_stock_alerts(db)


@router.get("/inventory/expiring-soon", response_model=List[MedicineInventoryResponse])
def get_expiring_soon_alerts(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "PHARMACY", "DEPARTMENT_HEAD"])),
):
    return pharmacy_service.get_expiring_soon(db, days=days)


@router.get("/inventory/{medicine_id}", response_model=MedicineInventoryResponse)
def get_medicine_inventory(
    medicine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return pharmacy_service.get_medicine(db, medicine_id)


@router.put("/inventory/{medicine_id}", response_model=MedicineInventoryResponse)
def update_medicine_inventory(
    medicine_id: int,
    obj_in: MedicineInventoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "PHARMACY"])),
):
    return pharmacy_service.update_medicine(db, medicine_id, obj_in)


@router.post("/dispense", response_model=PharmacyDispenseResponse, status_code=status.HTTP_201_CREATED)
def dispense_medicines(
    obj_in: PharmacyDispenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "PHARMACY"])),
):
    return pharmacy_service.dispense_medicines(db, current_user.id, obj_in)


@router.get("/dispensed", response_model=List[PharmacyDispenseResponse])
def list_dispensed_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    patient_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    history, _ = pharmacy_service.list_dispensed_history(db, skip=skip, limit=limit, patient_id=patient_id)
    return history

import math
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles, verify_patient_access
from app.services.billing_service import billing_service
from app.schemas.billing import BillingCreate, BillingUpdate, BillingResponse
from app.models.user import User

router = APIRouter(
    prefix="/billing",
    tags=["Billing"]
)


@router.post(
    "/",
    summary="Create Bill",
    status_code=status.HTTP_201_CREATED,
)
def create_bill(
    payload: BillingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "RECEPTIONIST"]))
):
    bill = billing_service.create_bill(db, payload)
    return {
        "success": True,
        "message": "Bill created successfully",
        "data": BillingResponse.model_validate(bill).model_dump()
    }


@router.get(
    "/",
    summary="Get Bills",
    status_code=status.HTTP_200_OK,
)
def get_bills(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    patient_id: Optional[int] = Query(None),
    payment_status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "RECEPTIONIST"]))
):
    items, total = billing_service.get_bills(
        db, page=page, limit=limit, patient_id=patient_id, payment_status=payment_status, search=search
    )
    pages = math.ceil(total / limit) if total > 0 else 1
    serialized = [BillingResponse.model_validate(b).model_dump() for b in items]
    return {
        "success": True,
        "message": "Bills fetched successfully",
        "data": {
            "items": serialized,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages
        }
    }


@router.get(
    "/{bill_id}",
    summary="Get Bill by ID",
    status_code=status.HTTP_200_OK,
)
def get_bill(
    bill_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bill = billing_service.get_bill_or_404(db, bill_id)
    verify_patient_access(current_user, bill.patient_id)
    return {
        "success": True,
        "message": "Bill details fetched successfully",
        "data": BillingResponse.model_validate(bill).model_dump()
    }


@router.get(
    "/patient/{patient_id}",
    summary="Get Patient Billing History",
    status_code=status.HTTP_200_OK,
)
def get_patient_history(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verify_patient_access(current_user, patient_id)
    items = billing_service.get_patient_history(db, patient_id)
    serialized = [BillingResponse.model_validate(b).model_dump() for b in items]
    return {
        "success": True,
        "message": "Patient billing history fetched successfully",
        "data": serialized
    }


@router.patch(
    "/{bill_id}",
    summary="Update Bill",
    status_code=status.HTTP_200_OK,
)
def update_bill(
    bill_id: str,
    payload: BillingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "RECEPTIONIST"]))
):
    bill = billing_service.update_bill(db, bill_id, payload)
    return {
        "success": True,
        "message": "Bill updated successfully",
        "data": BillingResponse.model_validate(bill).model_dump()
    }

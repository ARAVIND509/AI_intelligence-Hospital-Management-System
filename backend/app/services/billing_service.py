from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.billing_repository import billing_repository
from app.services.patient_service import patient_service
from app.schemas.billing import BillingCreate, BillingUpdate
from app.models.billing import Billing, BillItem
from app.utils.id_generator import generate_bill_id


class BillingService:
    def get_bill_or_404(self, db: Session, bill_id: str) -> Billing:
        bill = billing_repository.get_by_id_or_bill_id(db, bill_id)
        if not bill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bill '{bill_id}' not found"
            )
        return bill

    def create_bill(self, db: Session, payload: BillingCreate) -> Billing:
        patient_service.get_patient_or_404(db, payload.patient_id)

        bill_id = generate_bill_id(db)

        total_amount = 0.0
        db_items = []
        for item in payload.items:
            item_total = item.quantity * item.unit_price
            total_amount += item_total
            db_items.append({
                "item_name": item.item_name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_price": item_total,
            })

        net_amount = max(0.0, total_amount - payload.discount + payload.tax)

        db_bill = Billing(
            bill_id=bill_id,
            patient_id=payload.patient_id,
            appointment_id=payload.appointment_id,
            total_amount=total_amount,
            discount=payload.discount,
            tax=payload.tax,
            net_amount=net_amount,
            payment_status="unpaid",
            payment_method=payload.payment_method,
        )
        db.add(db_bill)
        db.flush()

        for item_data in db_items:
            db_item = BillItem(
                bill_id=db_bill.id,
                **item_data
            )
            db.add(db_item)

        db.commit()
        db.refresh(db_bill)
        return db_bill

    def get_bills(
        self,
        db: Session,
        page: int = 1,
        limit: int = 20,
        patient_id: Optional[int] = None,
        payment_status: Optional[str] = None,
        search: Optional[str] = None
    ):
        skip = (page - 1) * limit
        filters = {}
        if patient_id is not None:
            filters["patient_id"] = patient_id
        if payment_status is not None:
            filters["payment_status"] = payment_status

        items, total = billing_repository.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=filters,
            search_query=search,
            search_fields=["bill_id", "payment_status", "payment_method"]
        )
        return items, total

    def get_patient_history(self, db: Session, patient_id: int) -> List[Billing]:
        patient_service.get_patient_or_404(db, patient_id)
        return billing_repository.get_patient_history(db, patient_id)

    def update_bill(self, db: Session, bill_id: str, payload: BillingUpdate) -> Billing:
        bill = self.get_bill_or_404(db, bill_id)

        if payload.discount is not None:
            bill.discount = payload.discount
        if payload.tax is not None:
            bill.tax = payload.tax
        if payload.payment_status is not None:
            if payload.payment_status not in ["unpaid", "partially_paid", "paid", "cancelled"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid payment status '{payload.payment_status}'"
                )
            bill.payment_status = payload.payment_status
        if payload.payment_method is not None:
            bill.payment_method = payload.payment_method

        bill.net_amount = max(0.0, bill.total_amount - bill.discount + bill.tax)

        db.commit()
        db.refresh(bill)
        return bill


billing_service = BillingService()

import math
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.department_service import department_service
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse

router = APIRouter(
    prefix="/departments",
    tags=["Departments"]
)


@router.post(
    "/",
    summary="Create Department",
    status_code=status.HTTP_201_CREATED,
)
def create_department(payload: DepartmentCreate, db: Session = Depends(get_db)):
    dept = department_service.create_department(db, payload)
    return {
        "success": True,
        "message": "Department created successfully",
        "data": DepartmentResponse.model_validate(dept).model_dump()
    }


@router.get(
    "/",
    summary="Get All Departments",
    status_code=status.HTTP_200_OK,
)
def get_departments(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    items, total = department_service.get_departments(db, page=page, limit=limit, search=search)
    pages = math.ceil(total / limit) if total > 0 else 1
    serialized = [DepartmentResponse.model_validate(d).model_dump() for d in items]
    return {
        "success": True,
        "message": "Departments fetched successfully",
        "data": {
            "items": serialized,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages
        }
    }


@router.get(
    "/{department_id}",
    summary="Get Department by ID",
    status_code=status.HTTP_200_OK,
)
def get_department(department_id: int, db: Session = Depends(get_db)):
    dept = department_service.get_department_or_404(db, department_id)
    return {
        "success": True,
        "message": "Department details fetched successfully",
        "data": DepartmentResponse.model_validate(dept).model_dump()
    }


@router.patch(
    "/{department_id}",
    summary="Update Department",
    status_code=status.HTTP_200_OK,
)
def update_department(department_id: int, payload: DepartmentUpdate, db: Session = Depends(get_db)):
    dept = department_service.update_department(db, department_id, payload)
    return {
        "success": True,
        "message": "Department updated successfully",
        "data": DepartmentResponse.model_validate(dept).model_dump()
    }

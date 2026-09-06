from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.department_repository import department_repository
from app.schemas.department import DepartmentCreate, DepartmentUpdate
from app.models.department import Department


class DepartmentService:
    def get_department_or_404(self, db: Session, department_id: int) -> Department:
        dept = department_repository.get(db, department_id)
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Department with ID {department_id} not found"
            )
        return dept

    def create_department(self, db: Session, payload: DepartmentCreate) -> Department:
        existing = department_repository.get_by_name(db, payload.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Department with name '{payload.name}' already exists"
            )
        return department_repository.create(db, obj_in=payload)

    def get_departments(
        self,
        db: Session,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None
    ):
        skip = (page - 1) * limit
        items, total = department_repository.get_multi(
            db,
            skip=skip,
            limit=limit,
            search_query=search,
            search_fields=["name", "description"]
        )
        return items, total

    def update_department(self, db: Session, department_id: int, payload: DepartmentUpdate) -> Department:
        dept = self.get_department_or_404(db, department_id)
        if payload.name and payload.name != dept.name:
            existing = department_repository.get_by_name(db, payload.name)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Department with name '{payload.name}' already exists"
                )
        return department_repository.update(db, db_obj=dept, obj_in=payload)


department_service = DepartmentService()

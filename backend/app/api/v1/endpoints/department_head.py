from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.models.user import User
from app.services.department_head_service import department_head_service
from app.schemas.department_head import DepartmentOverviewResponse

router = APIRouter(prefix="/department-head", tags=["Department Head Dashboard"])


@router.get("/overview/{department_id}", response_model=DepartmentOverviewResponse)
def get_department_overview(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DEPARTMENT_HEAD"])),
):
    return department_head_service.get_department_overview(db, department_id)

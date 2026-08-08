from fastapi import APIRouter

router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)

@router.get("/")
async def get_patients():
    return {"message": "Patients API"}
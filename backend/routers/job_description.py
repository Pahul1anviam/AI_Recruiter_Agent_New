from fastapi import APIRouter
from backend.models.job_description import JobDescriptionRequest
from backend.services.job_description_service import generate_job_description

router = APIRouter()

@router.post("/generate_job_description")
def create_job_description(request: JobDescriptionRequest):
    return {"description": generate_job_description(request)}

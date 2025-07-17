from pydantic import BaseModel

class JobDescriptionRequest(BaseModel):
    job_title: str
    department: str
    responsibilities: str
    skills_required: str
    location: str
    experience_level: str

from backend.llm.llm_setup import get_job_description_chain
from backend.models.job_description import JobDescriptionRequest

def generate_job_description(request: JobDescriptionRequest) -> str:
    chain = get_job_description_chain()
    response = chain.run({
        "job_title": request.job_title,
        "department": request.department,
        "responsibilities": request.responsibilities,
        "skills_required": request.skills_required,
        "location": request.location,
        "experience_level": request.experience_level
    })
    return response.strip()

from pydantic import BaseModel

class CandidateScoreRequest(BaseModel):
    resume_text: str
    job_description: str

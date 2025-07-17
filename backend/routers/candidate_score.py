from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from backend.utils.pdf_loader_tool import load_pdf_text
from backend.services.candidate_score_service import score_candidate_match
import os

router = APIRouter()

@router.post("/score_candidate")
async def score_candidate(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    try:
        temp_path = f"temp_uploads/{resume.filename}"

        # Save uploaded file to disk
        with open(temp_path, "wb") as f:
            f.write(await resume.read())

        # Extract resume text from PDF
        resume_text = load_pdf_text(temp_path)

        # Score using Gemini
        result = score_candidate_match(resume_text=resume_text, job_description=job_description)

        # Clean up temp file
        os.remove(temp_path)

        return JSONResponse(content={"score": result})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from backend.utils.pdf_loader_tool import load_pdf_text
from backend.services.persona_builder_service import generate_persona_from_resume
import os

router = APIRouter()

@router.post("/generate_persona")
async def generate_persona(resume: UploadFile = File(...)):
    try:
        temp_path = f"temp_uploads/{resume.filename}"
        with open(temp_path, "wb") as f:
            f.write(await resume.read())

        resume_text = load_pdf_text(temp_path)
        persona = generate_persona_from_resume(resume_text)

        os.remove(temp_path)

        return JSONResponse(content={"persona": persona})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

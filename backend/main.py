from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import job_description, candidate_score, persona_builder, scheduler, slot_router 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict to ["http://localhost:8501"] for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Register the route
app.include_router(job_description.router)
app.include_router(candidate_score.router)
app.include_router(persona_builder.router)
app.include_router(scheduler.router, prefix="/scheduler", tags=["Scheduler"])
app.include_router(slot_router.router)

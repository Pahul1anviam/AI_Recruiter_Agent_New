from fastapi import APIRouter

router = APIRouter()

@router.get("/test_scheduler")
def test_scheduler():
    return {"message": "Scheduler route active"}

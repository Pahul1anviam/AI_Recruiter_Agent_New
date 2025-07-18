from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, date
from backend.services.calendar_service import get_available_slots, book_slot
from backend.services.lock_service import lock_slot, is_slot_locked
from backend.services.email_workflow_service import EmailWorkflowService

router = APIRouter()
workflow_service = EmailWorkflowService()

# Pydantic Models
class ShortlistRequest(BaseModel):
    candidate_email: EmailStr
    candidate_name: str
    job_title: str
    score: int

class AvailabilityRequest(BaseModel):
    candidate_email: EmailStr
    availability_date: str  # YYYY-MM-DD format

class SlotBookingRequest(BaseModel):
    candidate_email: EmailStr
    candidate_name: str
    slot_time: str  # ISO format
    slot_index: Optional[int] = None

# Step 1: Send shortlisting email
@router.post("/shortlist-candidate")
async def shortlist_candidate(request: ShortlistRequest):
    """
    Send shortlisting email to candidate asking for availability
    """
    try:
        # Store candidate in workflow
        workflow_service.store_candidate_workflow(
            candidate_email=request.candidate_email,
            candidate_name=request.candidate_name,
            job_title=request.job_title,
            score=request.score,
            status="shortlisted"
        )
        
        # Send shortlisting email
        success = workflow_service.send_shortlisting_email(
            candidate_email=request.candidate_email,
            candidate_name=request.candidate_name,
            job_title=request.job_title,
            score=request.score
        )
        
        if success:
            return {"message": f"Shortlisting email sent to {request.candidate_email}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send email")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Step 2: Handle availability response and send slots
@router.post("/send-available-slots")
async def send_available_slots(request: AvailabilityRequest):
    """
    Send available slots to candidate for their preferred date
    """
    try:
        # Get candidate workflow info
        candidate_info = workflow_service.get_candidate_workflow(request.candidate_email)
        if not candidate_info:
            raise HTTPException(status_code=404, detail="Candidate not found in workflow")
        
        # Get available slots for the date
        available_slots = get_available_slots(request.availability_date)
        
        if not available_slots:
            return {"message": "No slots available for the selected date"}
        
        # Send top 5 slots
        top_slots = available_slots[:5]
        success = workflow_service.send_slot_selection_email(
            candidate_email=request.candidate_email,
            candidate_name=candidate_info['candidate_name'],
            interview_date=request.availability_date,
            slots=top_slots
        )
        
        if success:
            # Update candidate status
            workflow_service.update_candidate_status(
                candidate_email=request.candidate_email,
                status="slots_sent"
            )
            return {
                "message": f"Available slots sent to {request.candidate_email}",
                "slots_sent": len(top_slots)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send slots email")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Step 3: Direct slot booking via URL (for email links)
@router.get("/book-slot")
async def book_slot_via_url(
    email: EmailStr = Query(...),
    slot: str = Query(...),
    name: str = Query(...)
):
    """
    Book slot directly via URL (called from email links)
    """
    try:
        # Check if slot is still available
        if is_slot_locked(slot):
            return HTMLResponse(content="""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2 style="color: #d32f2f;">❌ Slot Already Booked</h2>
                    <p>Sorry, this slot has already been booked by another candidate.</p>
                    <p>Please contact HR for alternative slots.</p>
                </body>
            </html>
            """, status_code=409)
        
        # Lock the slot
        if not lock_slot(slot):
            return HTMLResponse(content="""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2 style="color: #d32f2f;">❌ Slot Unavailable</h2>
                    <p>This slot is no longer available. Please try another slot.</p>
                </body>
            </html>
            """, status_code=409)
        
        # Book in Google Calendar
        try:
            meet_link = book_slot(
                candidate_name=name,
                candidate_email=email,
                start_time_str=slot
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Calendar booking failed: {str(e)}")
        
        # Send confirmation email
        success = workflow_service.send_confirmation_email(
            candidate_email=email,
            candidate_name=name,
            slot_time=slot,
            meet_link=meet_link
        )
        
        if success:
            # Update candidate status
            workflow_service.update_candidate_status(
                candidate_email=email,
                status="interview_scheduled"
            )
        
        return HTMLResponse(content=f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #2e7d32;">✅ Interview Scheduled!</h2>
                <p>Dear {name},</p>
                <p>Your interview has been successfully scheduled for:</p>
                <div style="background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <strong>Time:</strong> {slot}<br>
                    <strong>Meeting Link:</strong> <a href="{meet_link}">{meet_link}</a>
                </div>
                <p>A confirmation email has been sent to {email}</p>
                <p>Please join the meeting 5 minutes early.</p>
            </body>
        </html>
        """)
        
    except Exception as e:
        return HTMLResponse(content=f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #d32f2f;">❌ Booking Failed</h2>
                <p>Error: {str(e)}</p>
                <p>Please contact HR for assistance.</p>
            </body>
        </html>
        """, status_code=500)

# Step 4: API endpoint for slot booking (alternative to URL)
@router.post("/confirm-interview-slot")
async def confirm_interview_slot(request: SlotBookingRequest):
    """
    Confirm interview slot booking via API
    """
    try:
        # Check if slot is available
        if is_slot_locked(request.slot_time):
            raise HTTPException(status_code=409, detail="Slot already booked")
        
        # Lock the slot
        if not lock_slot(request.slot_time):
            raise HTTPException(status_code=409, detail="Failed to lock slot")
        
        # Book in Google Calendar
        meet_link = book_slot(
            candidate_name=request.candidate_name,
            candidate_email=request.candidate_email,
            start_time_str=request.slot_time
        )
        
        # Send confirmation email
        success = workflow_service.send_confirmation_email(
            candidate_email=request.candidate_email,
            candidate_name=request.candidate_name,
            slot_time=request.slot_time,
            meet_link=meet_link
        )
        
        if success:
            workflow_service.update_candidate_status(
                candidate_email=request.candidate_email,
                status="interview_scheduled"
            )
        
        return {
            "status": "success",
            "message": "Interview scheduled successfully",
            "meet_link": meet_link,
            "slot_time": request.slot_time
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Utility endpoints
@router.get("/candidate-status/{email}")
async def get_candidate_status(email: EmailStr):
    """
    Get candidate workflow status
    """
    candidate_info = workflow_service.get_candidate_workflow(email)
    if not candidate_info:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return candidate_info

@router.get("/available-slots/{date}")
async def get_available_slots_for_date(date: str):
    """
    Get available slots for a specific date
    """
    try:
        slots = get_available_slots(date)
        return {"date": date, "available_slots": slots}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Complete workflow trigger (for testing)
@router.post("/trigger-complete-workflow")
async def trigger_complete_workflow(request: ShortlistRequest):
    """
    Trigger complete workflow for testing - sends shortlisting email
    """
    try:
        # Store candidate
        workflow_service.store_candidate_workflow(
            candidate_email=request.candidate_email,
            candidate_name=request.candidate_name,
            job_title=request.job_title,
            score=request.score,
            status="shortlisted"
        )
        
        # Send shortlisting email
        success = workflow_service.send_shortlisting_email(
            candidate_email=request.candidate_email,
            candidate_name=request.candidate_name,
            job_title=request.job_title,
            score=request.score
        )
        
        if success:
            return {
                "message": "Workflow triggered successfully",
                "next_step": "Candidate will receive shortlisting email and should reply with availability",
                "candidate_email": request.candidate_email
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send email")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
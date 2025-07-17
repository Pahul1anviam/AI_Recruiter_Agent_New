import streamlit as st
import requests
import datetime

API_URL = "http://localhost:8000"  # FastAPI backend

st.title("📅 Interview Slot Booking (Candidate View)")

st.subheader("1. Fetch Available Slots")

if st.button("Get Available Slots"):
    res = requests.get(f"{API_URL}/calendar/available-slots")
    if res.status_code == 200:
        slots = res.json().get("available_slots", [])
        if not slots:
            st.warning("No available slots found.")
        else:
            st.session_state["slots"] = slots
            st.success(f"Found {len(slots)} slots")
    else:
        st.error("Failed to fetch available slots")

if "slots" in st.session_state:
    st.subheader("2. Select a Slot to Book")

    selected = st.selectbox("Choose a time slot:", st.session_state["slots"])
    candidate_name = st.text_input("Candidate Name", value="John Doe")
    candidate_email = st.text_input("Candidate Email", value="john.doe@example.com")

    if st.button("Book Slot"):
        booking_data = {
            "slot": selected,
            "candidate_name": candidate_name,
            "candidate_email": candidate_email
        }
        res = requests.post(f"{API_URL}/calendar/book-slot", json=booking_data)
        if res.status_code == 200:
            st.success("✅ Slot booked successfully!")
            st.write("Google Calendar Event Created and Candidate Added.")
        else:
            st.error(res.json().get("detail", "❌ Failed to book slot. Might be already booked."))

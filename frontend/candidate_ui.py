# candidate_ui.py
import streamlit as st
import requests

API_BASE = "http://localhost:8000"  # adjust if running on different port

st.title("🗓️ Interview Slot Booking")

st.markdown("Please enter your details to book an interview slot.")

# Step 1: Candidate info
name = st.text_input("Your Full Name")
email = st.text_input("Your Email")

if name and email:
    st.markdown("### Step 2: Choose a Time Slot")

    # Step 2: Fetch available slots
    try:
        res = requests.get(f"{API_BASE}/available-slots")
        slots = res.json().get("available_slots", [])
    except Exception as e:
        st.error("Error fetching slots from server.")
        st.stop()

    if not slots:
        st.warning("No slots available at the moment.")
        st.stop()

    # Show slot options
    selected_slot = st.selectbox("Available Time Slots", slots)

    if st.button("✅ Confirm Slot"):
        payload = {
            "candidate_name": name,
            "candidate_email": email,
            "slot_time": selected_slot,
        }
        try:
            r = requests.post(f"{API_BASE}/confirm-slot", json=payload)
            if r.status_code == 200:
                st.success("🎉 Your slot has been successfully booked!")
                meet_link = r.json().get("meet_link", "Check your email for details.")
                st.markdown(f"🔗 [Join Google Meet]({meet_link})")
            elif r.status_code == 409:
                st.error("Slot already booked. Please try another.")
            else:
                st.error(f"Error: {r.json().get('detail')}")
        except Exception as ex:
            st.error("Server error while booking slot.")

else:
    st.info("Please enter your name and email to continue.")

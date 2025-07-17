import streamlit as st
import requests


st.title("📅 Smart Interview Scheduler")

with st.form("schedule_form"):
    candidate_name = st.text_input("Candidate Name")
    candidate_score = st.number_input("Candidate Score", min_value=0, max_value=100)
    submitted = st.form_submit_button("Schedule Interview")

if submitted:
    if candidate_name.strip() and candidate_score:
        try:
            data = {"name": candidate_name, "score": int(candidate_score)}
            response = requests.post("http://localhost:8000/schedule_interview", data=data)
            result = response.json()

            if "scheduled_time" in result:
                st.success(f"✅ {result['message']}")
                st.markdown(f"**Candidate**: {result['candidate']}")
                st.markdown(f"**Score**: {result['score']}")
                st.markdown(f"**Scheduled Slot**: {result['scheduled_time']} to {result['ends_at']}")
            else:
                st.warning(result.get("message", "No slot available."))
        except Exception as e:
            st.error(f"Request failed: {e}")
    else:
        st.warning("Please fill in candidate name and score.")

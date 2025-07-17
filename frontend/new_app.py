import streamlit as st
import requests

st.set_page_config(page_title="Smart Interview Scheduler", page_icon="📅")
st.title("📅 Smart Interview Scheduler with Google Calendar Integration")

with st.form("schedule_form"):
    candidate_name = st.text_input("👤 Candidate Name")
    candidate_score = st.number_input("🎯 Candidate Score (0-100)", min_value=0, max_value=100)
    submitted = st.form_submit_button("✅ Schedule Interview")

if submitted:
    if candidate_name.strip() and candidate_score is not None:
        with st.spinner("Scheduling interview..."):
            try:
                data = {
                    "name": candidate_name,
                    "score": int(candidate_score)
                }

                response = requests.post("http://localhost:8000/schedule_interview", data=data)
                result = response.json()

                if "scheduled_time" in result:
                    st.success(result["message"])

                    st.markdown(f"**👤 Candidate**: `{result['candidate']}`")
                    st.markdown(f"**📊 Score**: `{result['score']}`")
                    st.markdown(f"**📅 Scheduled Slot**: `{result['scheduled_time']} to {result['ends_at']}`")

                    if "event_link" in result:
                        st.markdown(f"🔗 [📆 View on Google Calendar]({result['event_link']})")

                else:
                    st.warning(result.get("message", "No available slot found."))

            except Exception as e:
                st.error(f"❌ Error: {e}")
    else:
        st.warning("Please enter both candidate name and score.")

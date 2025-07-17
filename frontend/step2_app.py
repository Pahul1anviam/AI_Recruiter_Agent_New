import streamlit as st
import requests

st.title("🔍 Candidate Resume Relevance Scoring")

with st.form("score_form"):
    resume_pdf = st.file_uploader("Upload Resume PDF", type=["pdf"])
    job_description_input = st.text_area("Enter Job Description")

    submitted = st.form_submit_button("Evaluate Resume")

if submitted:
    if resume_pdf is not None and job_description_input.strip():
        try:
            files = {"resume": resume_pdf}
            data = {"job_description": job_description_input}

            response = requests.post("http://localhost:8000/score_candidate", files=files, data=data)
            result = response.json()

            if "score" in result:
                st.success("✅ Resume Scored Successfully")
                st.markdown(result["score"])
            else:
                st.error(result.get("error", "Unexpected error occurred"))

        except Exception as e:
            st.error(f"Error occurred: {e}")
    else:
        st.warning("Upload a resume and provide a job description.")

import streamlit as st
import requests

st.title("AI Job Description Generator")

with st.form("jd_form"):
    job_title = st.text_input("Job Title")
    department = st.text_input("Department")
    responsibilities = st.text_area("Responsibilities")
    skills_required = st.text_area("Skills Required")
    location = st.text_input("Location")
    experience_level = st.selectbox("Experience Level", ["Intern", "Junior", "Mid", "Senior", "Lead"])
    submitted = st.form_submit_button("Generate Job Description")

if submitted:
    payload = {
        "job_title": job_title,
        "department": department,
        "responsibilities": responsibilities,
        "skills_required": skills_required,
        "location": location,
        "experience_level": experience_level
    }

    try:
        response = requests.post("http://localhost:8000/generate_job_description", json=payload)
        result = response.json()
        st.subheader("Generated Job Description")
        st.code(result["description"])
    except Exception as e:
        st.error(f"Error: {e}")

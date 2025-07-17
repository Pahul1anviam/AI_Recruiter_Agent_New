import streamlit as st
import requests

st.title("👤 Candidate Persona Builder")

with st.form("persona_form"):
    resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    build_persona = st.form_submit_button("Generate Persona")

if build_persona:
    if resume_file is not None:
        try:
            files = {"resume": resume_file}
            response = requests.post("http://localhost:8000/generate_persona", files=files)
            result = response.json()

            if "persona" in result:
                st.subheader("AI-Generated Candidate Persona")
                st.markdown(result["persona"])
            else:
                st.error(result.get("error", "Unknown error"))
        except Exception as e:
            st.error(f"Request failed: {e}")
    else:
        st.warning("Please upload a resume PDF.")

import os
from typing import Any, Dict

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="ATS Resume Analyzer", page_icon="📄", layout="wide")

st.title("AI-Powered ATS Resume Analyzer")
st.caption("Upload a PDF resume, paste a job description, and get an LLM-based ATS evaluation.")

backend_url = os.getenv("FASTAPI_ANALYZE_URL", "http://127.0.0.1:8000/analyze")

with st.sidebar:
    st.subheader("Configuration")
    st.text_input("FastAPI /analyze URL", value=backend_url, key="backend_url")


resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
job_description = st.text_area(
    "Job Description",
    height=260,
    placeholder="Paste the target job description here...",
)


def render_results(data: Dict[str, Any]) -> None:
    st.subheader("ATS Evaluation")

    c1, c2, c3 = st.columns(3)
    c1.metric("ATS Score", f"{data.get('ATS_Score', 0)}/100")
    c2.metric("Technical Skills", f"{data.get('Technical_Skills_Score', 0)}/100")
    c3.metric("Experience", f"{data.get('Experience_Score', 0)}/100")

    c4, c5 = st.columns(2)
    c4.metric("Projects", f"{data.get('Projects_Score', 0)}/100")
    c5.metric("Education", f"{data.get('Education_Score', 0)}/100")

    st.markdown("### Profile Summary")
    st.write(data.get("Profile_Summary", "N/A"))

    st.markdown("### Matching Skills")
    st.write(data.get("Matching_Skills", []))

    st.markdown("### Missing Keywords")
    st.write(data.get("Missing_Keywords", []))

    st.markdown("### Strengths")
    st.write(data.get("Strengths", []))

    st.markdown("### Weaknesses")
    st.write(data.get("Weaknesses", []))

    st.markdown("### Improvement Suggestions")
    st.write(data.get("Improvement_Suggestions", []))

    with st.expander("Raw JSON Response"):
        st.json(data)


if st.button("Analyze", type="primary", use_container_width=True):
    if resume_file is None:
        st.error("Please upload a PDF resume.")
    elif not job_description.strip():
        st.error("Please provide a job description.")
    else:
        with st.spinner("Analyzing resume with LLM..."):
            try:
                files = {
                    "resume_file": (
                        resume_file.name,
                        resume_file.getvalue(),
                        "application/pdf",
                    )
                }
                data = {"job_description": job_description}
                response = requests.post(
                    st.session_state.backend_url,
                    files=files,
                    data=data,
                    timeout=120,
                )

                if response.status_code != 200:
                    try:
                        err = response.json()
                    except Exception:
                        err = {"detail": response.text}
                    st.error(f"Backend error: {err.get('detail', 'Unknown error')}")
                else:
                    render_results(response.json())
            except requests.RequestException as exc:
                st.error(f"Request failed: {exc}")

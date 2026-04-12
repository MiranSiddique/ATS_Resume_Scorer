from textwrap import dedent


def build_ats_prompt(resume_text: str, job_description: str) -> str:
    """Builds a strict JSON-only prompt for ATS evaluation."""
    return dedent(
        f"""
        You are an expert ATS and resume evaluator.

        Task:
        1) Compare the RESUME against the JOB DESCRIPTION.
        2) Score the resume for ATS relevance and quality.
        3) Return only valid JSON with the exact schema and keys below.

        Scoring Rules (0-100):
        - ATS_Score: overall alignment with role requirements.
        - Technical_Skills_Score: match of technologies, tools, and frameworks.
        - Experience_Score: relevance, depth, and impact of work experience.
        - Projects_Score: project relevance and measurable outcomes.
        - Education_Score: relevance and completeness of education credentials.

        JSON Schema (return exactly these keys):
        {{
          "ATS_Score": 0,
          "Technical_Skills_Score": 0,
          "Experience_Score": 0,
          "Projects_Score": 0,
          "Education_Score": 0,
          "Matching_Skills": [],
          "Missing_Keywords": [],
          "Strengths": [],
          "Weaknesses": [],
          "Improvement_Suggestions": [],
          "Profile_Summary": ""
        }}

        Output Constraints:
        - Output must be strict valid JSON.
        - Do not include markdown fences.
        - Do not include extra keys.
        - Arrays must contain concise strings.
        - Keep suggestions actionable and specific.

        JOB DESCRIPTION:
        {job_description}

        RESUME:
        {resume_text}
        """
    ).strip()

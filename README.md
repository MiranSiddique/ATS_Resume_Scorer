# ATS Resume Analyzer (FastAPI + Streamlit)

Production-ready AI-powered ATS Resume Analyzer that compares a resume PDF with a job description using an LLM and returns structured JSON.

## Features

- Upload Resume (PDF)
- Extract resume text
- Input Job Description
- LLM-based ATS evaluation (Gemini/OpenAI/Groq)
- Structured JSON output
- ATS score and sub-scores
- Matching skills and missing keywords
- Strengths, weaknesses, and actionable suggestions
- Profile summary

## Project Structure

```
ats_resume_project/
├── backend/
│   ├── main.py
│   ├── llm_service.py
│   ├── resume_parser.py
│   └── prompt.py
├── frontend/
│   └── app.py
├── .env
├── requirements.txt
└── README.md
```

## LLM JSON Output Schema

The backend enforces this exact response structure:

```json
{
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
}
```

## Setup

### 1) Create and activate virtual environment (Windows PowerShell)

```powershell
cd D:\Github_Projects\ATS_ML_Eval\ats_resume_project
python -m venv venv
.\venv\Scripts\Activate
```

### 2) Install dependencies

```powershell
pip install -r requirements.txt
```

### 3) Configure environment variables

Edit `.env` and set:

- `LLM_PROVIDER` as one of: `gemini`, `openai`, `groq`
- corresponding API key for your selected provider

Example for Gemini:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_real_key
```

## Run Backend (FastAPI)

```powershell
cd D:\Github_Projects\ATS_ML_Eval\ats_resume_project\backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Health check:

- `GET http://127.0.0.1:8000/health`

Analyze endpoint:

- `POST http://127.0.0.1:8000/analyze`
- form-data fields:
  - `resume_file`: PDF file
  - `job_description`: text

## Run Frontend (Streamlit)

```powershell
cd D:\Github_Projects\ATS_ML_Eval\ats_resume_project\frontend
streamlit run app.py
```

Open the Streamlit URL shown in terminal (default `http://localhost:8501`).

## API Example (cURL)

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -F "resume_file=@resume.pdf" \
  -F "job_description=We are hiring a Python backend engineer with FastAPI, Docker, and AWS experience..."
```

## Error Handling and Production Notes

- Rejects non-PDF files.
- Handles unreadable PDFs.
- Handles empty/invalid LLM responses.
- Validates LLM JSON with strict schema via Pydantic.
- Keeps LLM provider modular through `LLM_PROVIDER`.

For production deployment:

- Restrict `CORS_ORIGINS`.
- Use a process manager (e.g., systemd, supervisor, container orchestration).
- Add request logging and observability.
- Add auth/rate-limiting if exposed publicly.
- Add test suite (unit + integration) for CI.

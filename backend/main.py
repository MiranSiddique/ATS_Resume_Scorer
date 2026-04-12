import os
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from llm_service import LLMService, LLMServiceError
from prompt import build_ats_prompt
from resume_parser import ResumeParsingError, extract_text_from_pdf

load_dotenv()


class ATSAnalysisResult(BaseModel):
    ATS_Score: int = Field(ge=0, le=100)
    Technical_Skills_Score: int = Field(ge=0, le=100)
    Experience_Score: int = Field(ge=0, le=100)
    Projects_Score: int = Field(ge=0, le=100)
    Education_Score: int = Field(ge=0, le=100)
    Matching_Skills: List[str]
    Missing_Keywords: List[str]
    Strengths: List[str]
    Weaknesses: List[str]
    Improvement_Suggestions: List[str]
    Profile_Summary: str


app = FastAPI(title="ATS Resume Analyzer API", version="1.0.0")
llm_service = LLMService()

origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "ats-resume-analyzer"}


@app.post("/analyze", response_model=ATSAnalysisResult)
async def analyze_resume(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...),
) -> ATSAnalysisResult:
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")

    filename = (resume_file.filename or "").lower()
    if not filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Resume file must be a PDF.")

    try:
        file_bytes = await resume_file.read()
        resume_text = extract_text_from_pdf(file_bytes)
        prompt = build_ats_prompt(resume_text=resume_text, job_description=job_description)

        llm_output = llm_service.analyze_prompt(prompt)
        validated = ATSAnalysisResult.model_validate(llm_output)
        return validated
    except ResumeParsingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except LLMServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected server error: {exc}") from exc

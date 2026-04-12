import io
from typing import List

from PyPDF2 import PdfReader


class ResumeParsingError(Exception):
    """Raised when resume text cannot be extracted from PDF."""


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts text from a PDF byte stream."""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
    except Exception as exc:
        raise ResumeParsingError("Failed to read PDF file.") from exc

    pages_text: List[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            pages_text.append(text.strip())

    extracted = "\n\n".join(pages_text).strip()
    if not extracted:
        raise ResumeParsingError("No readable text found in the PDF resume.")

    return extracted

import json
import os
import re
from typing import Any, Dict

import requests


class LLMServiceError(Exception):
    """Raised for any LLM provider or response parsing error."""


class LLMService:
    def __init__(self) -> None:
        self.provider = os.getenv("LLM_PROVIDER", "gemini").lower().strip()

    def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        if self.provider == "gemini":
            raw = self._call_gemini(prompt)
        elif self.provider == "openai":
            raw = self._call_openai(prompt)
        elif self.provider == "groq":
            raw = self._call_groq(prompt)
        else:
            raise LLMServiceError(
                "Unsupported LLM_PROVIDER. Use one of: gemini, openai, groq."
            )

        return self._parse_json_response(raw)

    def _call_gemini(self, prompt: str) -> str:
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

        if not api_key:
            raise LLMServiceError("GEMINI_API_KEY is missing in environment variables.")

        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise LLMServiceError(
                "google-generativeai package is not installed for Gemini provider."
            ) from exc

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name=model_name)
            response = model.generate_content(prompt)
            text = getattr(response, "text", "") or ""
            if not text.strip():
                raise LLMServiceError("Gemini returned an empty response.")
            return text
        except Exception as exc:
            raise LLMServiceError(f"Gemini API call failed: {exc}") from exc

    def _call_openai(self, prompt: str) -> str:
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions")

        if not api_key:
            raise LLMServiceError("OPENAI_API_KEY is missing in environment variables.")

        payload = {
            "model": model,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": "Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
        }

        try:
            response = requests.post(
                url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as exc:
            raise LLMServiceError(f"OpenAI API call failed: {exc}") from exc

    def _call_groq(self, prompt: str) -> str:
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        model = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
        url = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1/chat/completions")

        if not api_key:
            raise LLMServiceError("GROQ_API_KEY is missing in environment variables.")

        payload = {
            "model": model,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": "Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
        }

        try:
            response = requests.post(
                url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as exc:
            raise LLMServiceError(f"Groq API call failed: {exc}") from exc

    def _parse_json_response(self, raw_text: str) -> Dict[str, Any]:
        if not raw_text or not raw_text.strip():
            raise LLMServiceError("LLM returned empty output.")

        text = raw_text.strip()

        # Gracefully handle fenced JSON if a provider ignores instructions.
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\\s*", "", text)
            text = re.sub(r"\\s*```$", "", text)

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise LLMServiceError("Failed to parse JSON response from LLM.") from exc

        if not isinstance(parsed, dict):
            raise LLMServiceError("LLM response JSON must be an object.")

        return parsed

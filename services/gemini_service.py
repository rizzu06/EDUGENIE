import json
import re
from functools import lru_cache

from config import get_settings


class GeminiServiceError(RuntimeError):
    pass


def clean_json_block(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


@lru_cache
def get_client():
    from google import genai
    settings = get_settings()
    if not settings.gemini_api_key:
        raise GeminiServiceError(
            "GEMINI_API_KEY is not configured. Add it to your .env file to use this feature."
        )
    return genai.Client(api_key=settings.gemini_api_key)


def _generate_config(*, temperature: float, response_mime_type: str | None = None):
    from google.genai import types

    kwargs = {
        "temperature": temperature,
        "system_instruction": (
            "You are EduGenie, a concise and accurate educational assistant. "
            "Explain ideas clearly, avoid unnecessary jargon, and say when uncertainty exists."
        ),
    }
    if response_mime_type:
        kwargs["response_mime_type"] = response_mime_type
    return types.GenerateContentConfig(**kwargs)


def generate_text(prompt: str, *, temperature: float = 0.4) -> str:
    settings = get_settings()
    try:
        response = get_client().models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=_generate_config(temperature=temperature),
        )
    except Exception as exc:
        raise GeminiServiceError(f"Gemini request failed: {exc}") from exc

    text = getattr(response, "text", None)
    if not text:
        raise GeminiServiceError("Gemini returned an empty response.")
    return text.strip()


def generate_json(prompt: str) -> dict:
    settings = get_settings()
    try:
        response = get_client().models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=_generate_config(temperature=0.3, response_mime_type="application/json"),
        )
    except Exception as exc:
        raise GeminiServiceError(f"Gemini request failed: {exc}") from exc

    text = getattr(response, "text", None)
    if not text:
        raise GeminiServiceError("Gemini returned an empty JSON response.")
    try:
        return json.loads(clean_json_block(text))
    except json.JSONDecodeError as exc:
        raise GeminiServiceError(f"Gemini returned invalid JSON: {exc}") from exc

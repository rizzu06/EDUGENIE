from functools import lru_cache

from config import get_settings


class LocalExplanationError(RuntimeError):
    pass


@lru_cache
def _load_local_pipeline():
    settings = get_settings()
    if not settings.enable_local_explanation:
        return None
    try:
        from transformers import pipeline
        return pipeline(
            "text2text-generation",
            model=settings.local_explanation_model,
            device=-1,
        )
    except Exception as exc:
        raise LocalExplanationError(f"Could not load local explanation model: {exc}") from exc


def explain_concept(topic: str) -> str:
    settings = get_settings()
    if not settings.enable_local_explanation:
        from services.gemini_service import generate_text
        return generate_text(
            f"Explain the concept '{topic}' to a beginner using a simple analogy and one example."
        )

    try:
        generator = _load_local_pipeline()
        prompt = (
            "Explain the following educational concept to a beginner. "
            "Use simple language, a short analogy, and one example. Keep it concise.\n\n"
            f"Concept: {topic}"
        )
        output = generator(prompt, max_new_tokens=180, do_sample=False)
        text = output[0]["generated_text"].strip()
        if not text:
            raise LocalExplanationError("Local model returned an empty response.")
        return text
    except Exception:
        # The project remains usable when the optional local model cannot be loaded.
        from services.gemini_service import generate_text
        return generate_text(
            f"Explain the concept '{topic}' to a beginner using a simple analogy and one example."
        )

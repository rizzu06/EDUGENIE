from services.gemini_service import generate_text


def summarize_text(text: str) -> str:
    prompt = f"""Summarize the educational passage below for quick revision.
Preserve the core facts and relationships, remove redundancy, and use clear language.
Return a short title followed by 5-8 concise bullet points when the passage is long.

PASSAGE:
{text}
"""
    return generate_text(prompt, temperature=0.2)

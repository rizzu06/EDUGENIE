from pydantic import ValidationError

from schemas import QuizResponse
from services.gemini_service import GeminiServiceError, generate_json


def generate_quiz(passage: str, num_questions: int = 3) -> QuizResponse:
    prompt = f"""Generate exactly {num_questions} multiple-choice questions from the passage below.
Each question must contain exactly four options and one correct answer.
The correct_answer must exactly match one option.
Include a brief explanation for the correct answer.

JSON schema:
{{
  "questions": [
    {{
      "question": "...",
      "options": ["...", "...", "...", "..."],
      "correct_answer": "...",
      "explanation": "..."
    }}
  ]
}}

PASSAGE:
{passage}
"""
    try:
        payload = generate_json(prompt)
        result = QuizResponse.model_validate(payload)
    except ValidationError as exc:
        raise GeminiServiceError(f"Quiz validation failed: {exc}") from exc

    if len(result.questions) != num_questions:
        raise GeminiServiceError(
            f"Quiz model returned {len(result.questions)} questions; expected {num_questions}."
        )
    for item in result.questions:
        if item.correct_answer not in item.options:
            raise GeminiServiceError("Quiz contained a correct answer not present in its options.")
    return result

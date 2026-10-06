from services.gemini_service import generate_text


def answer_question(question: str, context: str = "") -> str:
    context_section = f"\nOptional context:\n{context}\n" if context else ""
    prompt = f"""Answer the student's question accurately and at an appropriate educational level.
Question: {question}
{context_section}
Requirements:
- Give the direct answer first.
- Then explain the reasoning in simple language.
- Use bullets or a short example when useful.
- Do not invent facts or citations.
"""
    return generate_text(prompt)

from services.gemini_service import generate_text


def get_learning_recommendations(topic: str, level: str = "beginner", timeframe: str = "8 weeks") -> str:
    prompt = f"""Create a personalized learning path for: {topic}
Learner level: {level}
Suggested timeframe: {timeframe}

Structure the response as:
1. Goal
2. Prerequisites
3. Week-by-week or phase-by-phase progression from beginner to advanced where appropriate
4. Practice activities/projects
5. Revision checkpoints
6. Suggested resource types (videos, articles, books, documentation)
7. How to know the learner is ready for the next level

Keep it practical and adaptable. Do not fabricate specific URLs.
"""
    return generate_text(prompt, temperature=0.5)

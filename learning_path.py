from gemini_client import generate


def get_learning_recommendations(topic: str) -> str:
    prompt = f"""
Create a personalized learning path for this topic:

{topic}

Assume the learner is a beginner unless the input says otherwise.
Organize the plan from beginner to advanced.
For each stage include:
- Topics to learn
- What the learner should be able to do
- Suggested time
- Useful resource types (videos, documentation, books, practice)

End with a simple practice/project suggestion.
Do not invent specific URLs.
"""
    return generate(prompt)

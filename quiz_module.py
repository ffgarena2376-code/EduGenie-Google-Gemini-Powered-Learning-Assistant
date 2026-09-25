import json
import re

from gemini_client import generate


def _clean_json_block(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def generate_quiz(text: str) -> list:
    prompt = f"""
Create exactly 3 multiple-choice questions from the educational text below.

Return ONLY valid JSON. No Markdown and no explanation.
The JSON must be an object with this exact shape:
{{
  "questions": [
    {{
      "question": "string",
      "options": ["string", "string", "string", "string"],
      "correct_answer": "string"
    }}
  ]
}}

Rules:
- Exactly 3 questions.
- Exactly 4 options per question.
- correct_answer must exactly match one option.
- Questions must be answerable from the supplied text.
- Make distractors plausible.

Educational text:
{text}
"""
    raw = _clean_json_block(generate(prompt))
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Quiz JSON parsing failed: {exc}")

    questions = data.get("questions")
    if not isinstance(questions, list) or len(questions) != 3:
        raise RuntimeError("Gemini did not return exactly 3 questions.")

    for q in questions:
        if not isinstance(q, dict):
            raise RuntimeError("Invalid quiz question.")
        if not isinstance(q.get("options"), list) or len(q["options"]) != 4:
            raise RuntimeError("Each quiz question must have 4 options.")
        if q.get("correct_answer") not in q["options"]:
            raise RuntimeError("correct_answer must match an option.")

    return questions

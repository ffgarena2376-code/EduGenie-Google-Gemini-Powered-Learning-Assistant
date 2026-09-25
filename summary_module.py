from gemini_client import generate


def summarize_text(text: str) -> str:
    prompt = f"""
Summarize the following educational text for quick revision.

Requirements:
- Keep the main facts and important concepts.
- Remove repetition and unnecessary wording.
- Use simple language.
- Prefer short paragraphs or bullet points.

Text:
{text}
"""
    return generate(prompt)

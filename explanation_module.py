from gemini_client import generate


def explain_topic(topic: str) -> str:
    prompt = f"""
Explain the following topic to a beginner.

Topic:
{topic}

Use this structure:
1. Simple definition
2. How it works
3. Easy real-world example
4. Key points to remember

Keep the language clear, short, and educational.
"""
    return generate(prompt)

import os
import json
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load .env manually - no python-dotenv needed
def load_env():
    env_file = os.path.join(BASE_DIR, ".env")
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                os.environ.setdefault(key, value)

load_env()

API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")


def ask_gemini(prompt):
    if not API_KEY:
        raise Exception("GEMINI_API_KEY is missing from .env")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    request = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": API_KEY
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            result = json.loads(response.read().decode("utf-8"))

        candidates = result.get("candidates", [])
        if not candidates:
            raise Exception("Gemini returned no answer.")

        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(part.get("text", "") for part in parts)

        if not text:
            raise Exception("Gemini returned an empty answer.")

        return text

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="ignore")
        raise Exception(f"Gemini API error {e.code}: {error_body}")
    except urllib.error.URLError as e:
        raise Exception(f"Internet connection error: {e}")


def clean_json_text(text):
    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    return text


def generate_quiz(topic):
    prompt = f"""
You are EduGenie, an educational assistant.

Create exactly 3 multiple-choice questions about:
{topic}

Rules:
- Exactly 3 questions
- Exactly 4 options for every question
- Only one correct answer
- Suitable for a student
- Return ONLY valid JSON
- Do not use markdown

JSON format:
{{
  "questions": [
    {{
      "question": "Question text",
      "options": ["A", "B", "C", "D"],
      "answer": "A"
    }}
  ]
}}
"""

    text = ask_gemini(prompt)
    text = clean_json_text(text)

    try:
        quiz = json.loads(text)

        if "questions" not in quiz:
            raise ValueError("Missing questions")

        if len(quiz["questions"]) != 3:
            raise ValueError("Quiz does not contain exactly 3 questions")

        for q in quiz["questions"]:
            if len(q.get("options", [])) != 4:
                raise ValueError("A question does not have 4 options")

        return quiz

    except Exception:
        # Fallback if model returns imperfect JSON
        return {
            "questions": [
                {
                    "question": "Quiz generation returned an unexpected format. Please try again.",
                    "options": ["Try again", "Close", "Refresh", "None"],
                    "answer": "Try again"
                },
                {
                    "question": "What is the main purpose of EduGenie?",
                    "options": [
                        "Learning assistance",
                        "Gaming",
                        "Shopping",
                        "Banking"
                    ],
                    "answer": "Learning assistance"
                },
                {
                    "question": "How many questions are normally generated?",
                    "options": ["1", "2", "3", "10"],
                    "answer": "3"
                }
            ]
        }


def handle_task(task, text):
    if not text.strip():
        raise Exception("Please enter a topic or question.")

    if task == "qa":
        prompt = f"""
You are EduGenie, a helpful educational assistant.

Answer the student's question clearly and accurately.

Student question:
{text}

Explain the answer in simple language.
Use examples when useful.
"""

    elif task == "explain":
        prompt = f"""
You are EduGenie, an educational assistant.

Explain the following topic in simple language so a student can understand it easily.

Topic:
{text}

Include:
1. Simple definition
2. How it works
3. Important keywords
4. Simple example
5. Short summary
"""

    elif task == "summarize":
        prompt = f"""
You are EduGenie, an educational assistant.

Summarize the following text for a student.

Text:
{text}

Give:
- Main idea
- Important points
- Important keywords
- Short final summary
"""

    elif task == "recommend":
        prompt = f"""
You are EduGenie, a personalized learning assistant.

Create a simple learning path for:
{text}

Give:
1. What to learn first
2. What to learn next
3. Practice activities
4. Suggested project/practice
5. What to learn after that

Keep it practical and student-friendly.
"""

    elif task == "quiz":
        return generate_quiz(text)

    else:
        raise Exception("Unknown task.")

    return ask_gemini(prompt)


HTML = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EduGenie - Learning Assistant</title>
<style>
* { box-sizing: border-box; }

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: linear-gradient(135deg, #eef2ff, #f8fafc);
    color: #1e293b;
}

.container {
    width: 94%;
    max-width: 850px;
    margin: 25px auto;
}

.header {
    background: #4f46e5;
    color: white;
    padding: 25px;
    border-radius: 18px;
    text-align: center;
    box-shadow: 0 8px 25px rgba(0,0,0,0.12);
}

.header h1 {
    margin: 0 0 8px;
    font-size: 30px;
}

.header p {
    margin: 0;
    opacity: 0.9;
}

.card {
    background: white;
    margin-top: 20px;
    padding: 22px;
    border-radius: 18px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.08);
}

label {
    display: block;
    font-weight: bold;
    margin-bottom: 8px;
}

select, textarea, button {
    width: 100%;
    font-size: 16px;
    border-radius: 10px;
}

select, textarea {
    border: 1px solid #cbd5e1;
    padding: 12px;
}

textarea {
    min-height: 150px;
    resize: vertical;
    margin-top: 8px;
}

button {
    margin-top: 15px;
    padding: 13px;
    border: none;
    background: #4f46e5;
    color: white;
    font-weight: bold;
    cursor: pointer;
}

button:hover {
    background: #4338ca;
}

#status {
    margin-top: 15px;
    font-weight: bold;
}

#result {
    margin-top: 15px;
    padding: 18px;
    background: #f8fafc;
    border-radius: 12px;
    white-space: pre-wrap;
    line-height: 1.6;
}

.question {
    background: white;
    padding: 15px;
    margin-bottom: 15px;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
}

.option {
    display: block;
    padding: 9px;
    margin: 7px 0;
    background: #f1f5f9;
    border-radius: 7px;
}

.footer {
    text-align: center;
    margin: 20px;
    color: #64748b;
}
</style>
</head>

<body>
<div class="container">

<div class="header">
    <h1>🎓 EduGenie</h1>
    <p>Google Gemini Powered Learning Assistant</p>
</div>

<div class="card">

<label for="task">Choose a task</label>

<select id="task">
    <option value="explain">Explain</option>
    <option value="qa">QnA</option>
    <option value="quiz">Quiz</option>
    <option value="summarize">Summary</option>
    <option value="recommend">Recommend Learning Path</option>
</select>

<br><br>

<label for="input">Enter your topic, question or text</label>

<textarea id="input" placeholder="Example: Explain machine learning in simple words"></textarea>

<button onclick="generate()">Generate</button>

<div id="status"></div>
<div id="result"></div>

</div>

<div class="footer">
    EduGenie • AI Learning Assistant
</div>

</div>

<script>
async function generate() {

    const task = document.getElementById("task").value;
    const text = document.getElementById("input").value.trim();
    const status = document.getElementById("status");
    const result = document.getElementById("result");

    if (!text) {
        status.innerText = "Please enter something first.";
        return;
    }

    status.innerText = "⏳ EduGenie is thinking...";
    result.innerHTML = "";

    try {

        const response = await fetch("/api", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                task: task,
                text: text
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Something went wrong.");
        }

        status.innerText = "✅ Done";

        if (task === "quiz" && data.result.questions) {

            let html = "";

            data.result.questions.forEach((q, index) => {

                html += `<div class="question">`;
                html += `<b>${index + 1}. ${escapeHtml(q.question)}</b>`;

                q.options.forEach(option => {
                    html += `<div class="option">${escapeHtml(option)}</div>`;
                });

                html += `<small><b>Answer:</b> ${escapeHtml(q.answer)}</small>`;
                html += `</div>`;
            });

            result.innerHTML = html;

        } else {

            result.innerText = data.result;
        }

    } catch (error) {

        status.innerText = "❌ Error";
        result.innerText = error.message;
    }
}

function escapeHtml(text) {
    return String(text)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}
</script>

</body>
</html>
"""


class EduGenieHandler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        self.wfile.write(body)

    def do_GET(self):

        path = urlparse(self.path).path

        if path == "/" or path == "/index.html":

            body = HTML.encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()

            self.wfile.write(body)

        elif path == "/health":

            self.send_json({
                "status": "ok",
                "project": "EduGenie",
                "model": MODEL
            })

        else:
            self.send_json({"error": "Page not found"}, 404)

    def do_POST(self):

        path = urlparse(self.path).path

        if path != "/api":
            self.send_json({"error": "Endpoint not found"}, 404)
            return

        try:

            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)

            data = json.loads(body.decode("utf-8"))

            task = data.get("task", "")
            text = data.get("text", "")

            result = handle_task(task, text)

            self.send_json({
                "success": True,
                "result": result
            })

        except Exception as e:

            self.send_json({
                "success": False,
                "error": str(e)
            }, 500)

    def log_message(self, format, *args):
        print("[EduGenie]", format % args)


def main():
    host = "0.0.0.0"
    port = 8000

    print("")
    print("======================================")
    print("        🎓 EduGenie Started")
    print("======================================")
    print("")
    print(f"Model: {MODEL}")
    print("")
    print("Open this in your phone browser:")
    print("http://127.0.0.1:8000")
    print("")
    print("Press CTRL+C to stop.")
    print("")

    server = HTTPServer((host, port), EduGenieHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()

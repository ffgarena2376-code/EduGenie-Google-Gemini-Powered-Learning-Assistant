# EduGenie on Termux

## 1. Install Termux
Use the official F-Droid/GitHub Termux distribution rather than an outdated Play Store build.

## 2. Update packages
```bash
pkg update && pkg upgrade
```

## 3. Install Python and Git
```bash
pkg install python git
```

Check Python:
```bash
python --version
```

## 4. Create/open the project
Put the EduGenie folder somewhere accessible in Termux, then:
```bash
cd EduGenie
```

## 5. Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
```

If activation is inconvenient, you can run the environment's Python directly:
```bash
.venv/bin/python --version
```

## 6. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 7. Configure Gemini
Create `.env` from `.env.example`:
```bash
cp .env.example .env
nano .env
```

Replace:
```text
GEMINI_API_KEY=your_api_key_here
```
with your real API key.

Save nano with:
- Ctrl+O
- Enter
- Ctrl+X

Never share your `.env` file or API key.

## 8. Run EduGenie
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Then open your phone browser:
```text
http://127.0.0.1:8000
```

## 9. Test the API
Health check:
```bash
curl http://127.0.0.1:8000/health
```

Expected:
```json
{"status":"ok","service":"EduGenie"}
```

API documentation:
```text
http://127.0.0.1:8000/docs
```

## 10. Stop the server
Press:
```text
Ctrl+C
```

## Notes for Android/Termux
The original project document describes a local LaMini-Flan-T5 model for explanations and Gemini 1.5 Pro for other tasks. This Termux version uses the current Google GenAI Python SDK and Gemini for all five functions so the project stays practical on a phone and does not require downloading a large local ML model.

The five documented functions are preserved:
- Q&A
- Explanation
- Quiz generation
- Summarization
- Learning recommendations

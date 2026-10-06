# EduGenie — Google Gemini Powered Learning Assistant

EduGenie is a lightweight educational assistant based on the supplied project documentation. It provides:

- Question answering (`/qa`)
- Concept explanation (`/explain`)
- Three-or-more question MCQ generation (`/quiz`)
- Educational summarization (`/summarize`)
- Personalized learning paths (`/learn/recommendations`)

The original documentation specifies FastAPI, HTML/CSS, Gemini for Q&A/summary/quiz/learning paths, and LaMini-Flan-T5 for concept explanations. The implementation below keeps those module boundaries while using Google's current `google-genai` Python SDK. The Gemini model is configurable through `.env` rather than being fixed to the older Gemini 1.5 Pro name in the 2025 documentation.

## 1. Project structure

```text
EduGenie/
├── app/
│   └── __init__.py
├── services/
│   ├── __init__.py
│   ├── explanation_module.py
│   ├── gemini_service.py
│   ├── learning_path.py
│   ├── qna.py
│   ├── quiz_module.py
│   └── summary_module.py
├── static/
│   ├── app.js
│   └── style.css
├── templates/
│   └── index.html
├── tests/
│   └── test_api.py
├── .env.example
├── .gitignore
├── .vscode/
│   ├── extensions.json
│   ├── launch.json
│   └── settings.json
├── config.py
├── main.py
├── requirements.txt
└── README.md
```

## 2. Prerequisites

- Python 3.10+
- A Google AI Studio API key for Gemini-backed features
- VS Code is recommended

The supplied documentation lists Python 3.10+, FastAPI, HTML/CSS, a Gemini API key, Uvicorn and Jinja2 as prerequisites.

## 3. Create the environment

### Windows PowerShell

```powershell
cd EduGenie
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

### macOS/Linux

```bash
cd EduGenie
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

## 4. Configure Gemini

Open `.env` and set:

```env
GEMINI_API_KEY=your_real_key_here
GEMINI_MODEL=gemini-3.8-flash
```

The application reads the key from the environment and never places it in browser JavaScript.

If your account/project uses another supported Gemini model, change only `GEMINI_MODEL`.

## 5. Local explanation model

The project documentation names `MBZUAI/LaMini-Flan-T5-783M` for concept explanations. The implementation loads it lazily on the first `/explain` request, so startup does not immediately download the model.

For a machine that is too small for the local model, set:

```env
ENABLE_LOCAL_EXPLANATION=false
```

Then `/explain` uses Gemini instead. This keeps the application functional without requiring a large local model download.

## 6. Run

From the project root with the virtual environment activated:

```bash
uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

FastAPI interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

## 7. API examples

### Q&A

```bash
curl -X POST http://127.0.0.1:8000/qa ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"Which is the largest ocean?\"}"
```

### Explain

```bash
curl -X POST http://127.0.0.1:8000/explain ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"Pythagoras theorem\"}"
```

### Quiz

```bash
curl -X POST http://127.0.0.1:8000/quiz ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"The Earth revolves around the Sun.\",\"num_questions\":3}"
```

### Summary

```bash
curl -X POST http://127.0.0.1:8000/summarize ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"Paste a long educational passage here.\"}"
```

### Learning path

```bash
curl -X POST http://127.0.0.1:8000/learn/recommendations ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"SQL\",\"level\":\"beginner\",\"timeframe\":\"8 weeks\"}"
```

## 8. Test

Run:

```bash
pytest -q
```

The included tests use mocked AI service functions, so they do not spend API quota or require a live Gemini request.

## 9. VS Code

1. Open the `EduGenie` folder in VS Code.
2. Install the recommended Python/Pylance extensions.
3. Select `.venv` as the Python interpreter.
4. Copy `.env.example` to `.env` and set `GEMINI_API_KEY`.
5. Open the Run and Debug panel.
6. Choose `EduGenie: FastAPI` and start debugging.
7. Alternatively use the integrated terminal and run `uvicorn main:app --reload`.

## 10. Troubleshooting

### `GEMINI_API_KEY is not configured`

Confirm `.env` exists in the project root and contains a valid key, then restart Uvicorn.

### Gemini model unavailable

Change `GEMINI_MODEL` to a model currently enabled for your Google AI account/project. The application intentionally keeps this setting configurable.

### `/explain` downloads a model or is slow

The LaMini model is loaded lazily and may download model weights on first use. For a lightweight setup, set `ENABLE_LOCAL_EXPLANATION=false`.

### Port already in use

Run:

```bash
uvicorn main:app --reload --port 8001
```

Then open `http://127.0.0.1:8001`.

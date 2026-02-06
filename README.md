# Document Analysis API

A simple API to analyze PDF and Word documents using Groq LLM.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your Groq API key:
```
GROQ_API_KEY=your_key_here
```

## Run

```bash
python main.py
```

The API will be at `http://localhost:8000`

## Usage

Upload a document to analyze:
```bash
curl -X POST "http://localhost:8000/analyze" -F "file=@your_document.pdf"
```

Or just open `http://localhost:8000/docs` in your browser to use the interactive API.

## Files

- `main.py` - FastAPI endpoints
- `workflow.py` - LangGraph analysis workflow
- `parser.py` - PDF/Word text extraction
- `chunker.py` - Document chunking
- `models.py` - Response schemas
- `config.py` - Settings

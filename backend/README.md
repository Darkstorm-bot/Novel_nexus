# Narrative Nexus Backend

AI-powered collaborative story writing platform.

## Setup

### Prerequisites
- Python 3.10+
- pip

### Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy environment file:
```bash
cp .env.example .env
```

4. Run the application:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Testing

```bash
pytest
```

## Project Structure

```
backend/
├── app/
│   ├── agents/          # AI agents for pipeline phases
│   ├── api/             # API endpoints
│   ├── core/            # Core utilities (logging, exceptions)
│   ├── memory/          # Three-layer memory system
│   ├── schemas/         # Pydantic models
│   ├── state_machine/   # Pipeline state machine
│   ├── utils/           # Utility functions
│   └── main.py          # FastAPI application
├── config/              # Configuration
├── tests/               # Tests
└── requirements.txt     # Dependencies
```

## API Documentation

Once running, access Swagger UI at: http://localhost:8000/docs

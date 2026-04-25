# Narrative Nexus V4.0

**AI-Powered Collaborative Story Writing Platform with MemPalace Memory System**

A sophisticated full-stack application that leverages Large Language Models (LLMs) to assist writers in creating novels through a structured 9-phase pipeline. Features **MemPalace integration** for advanced memory management, real-time collaboration, memory-consistent character tracking, and a beautiful modern UI.

![Status](https://img.shields.io/badge/status-ready-green)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![React](https://img.shields.io/badge/react-18+-61dafb)
![License](https://img.shields.io/badge/license-MIT-blue)

---

## 🌟 Features

### Core Capabilities
- **9-Phase Writing Pipeline**: Concept → Outline → Beats → Draft → Critique → Rewrite → Polish → Consistency → Export
- **AI Agent System**: Specialized agents for each phase using LiteLLM/Ollama/LM Studio
- **MemPalace Memory System**: Advanced long-term memory with ChromaDB vector storage
- **LM Studio Integration**: Run local LLMs privately with OpenAI-compatible API
- **Real-Time Collaboration**: WebSocket-powered live updates and diff visualization
- **Character State Tracking**: Automatic consistency checking across the entire narrative
- **Human-in-the-Loop**: Approval gates at every critical phase transition
- **Story Consistency Checking**: AI-powered detection of plot holes and anachronisms
- **Entity Extraction**: Automatic identification of characters, locations, and objects

### Tech Stack
| Component | Technology |
|-----------|------------|
| **Backend** | Python 3.10+, FastAPI, Pydantic v2, Uvicorn |
| **Frontend** | React 18, TypeScript, Vite, TailwindCSS v4 |
| **Database** | ChromaDB (Vector), SQLite/PostgreSQL (Relational) |
| **Memory System** | MemPalace v3.3+ |
| **State Machine** | `transitions` library |
| **LLM Integration** | LiteLLM, Ollama, MemPalace, LM Studio |
| **Local LLM** | LM Studio, Ollama |
| **Real-time** | WebSockets |
| **Export** | EbookLib, WeasyPrint |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Node.js 18+ and npm
- Git
- LM Studio or Ollama (for local LLM inference)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd narrative-nexus
```

### 2. Backend Setup

#### Create Virtual Environment
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Configure Environment
Create a `.env` file in the `backend` directory:
```env
# LLM Configuration
LITELLM_API_KEY=your_api_key_here
OLLAMA_HOST=http://localhost:11434

# Database
CHROMA_PERSIST_DIR=./chroma_db
DATABASE_URL=sqlite:///./narrative_nexus.db

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

#### Run Backend
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Access Swagger docs at: `http://localhost:8000/docs`

### 3. Frontend Setup

#### Install Dependencies
```bash
cd frontend
npm install
```

#### Configure Environment
Create a `.env` file in the `frontend` directory:
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

#### Run Frontend
```bash
npm run dev
```
Access the app at: `http://localhost:5173`

---

## 🏗️ Project Structure

```
narrative-nexus/
├── backend/
│   ├── app/
│   │   ├── api/            # API Routes
│   │   ├── core/           # Config, Security, Logging
│   │   ├── models/         # Pydantic & DB Models
│   │   ├── services/       # Business Logic
│   │   ├── agents/         # LLM Agent Implementations
│   │   ├── pipeline/       # State Machine & Orchestrator
│   │   ├── memory/         # Vector & Episodic Memory
│   │   └── main.py         # App Entry Point
│   ├── tests/              # Pytest Suite
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── api/            # Axios Client & WS
│   │   ├── components/     # Reusable UI Components
│   │   ├── pages/          # Page Views
│   │   ├── stores/         # Zustand State Management
│   │   ├── types/          # TypeScript Definitions
│   │   ├── utils/          # Helpers
│   │   └── App.tsx
│   ├── public/
│   ├── package.json
│   └── .env
├── docker-compose.yml
└── README.md
```

---

## 🛠️ Common Errors & Solutions

### Backend Issues

#### 1. `ModuleNotFoundError: No module named 'app'`
**Cause**: Running uvicorn from the wrong directory.
**Solution**:
```bash
cd backend
uvicorn app.main:app --reload
```

#### 2. `ChromaDB Connection Error`
**Cause**: Missing persistence directory or permission issues.
**Solution**:
```bash
# Ensure directory exists
mkdir -p backend/chroma_db
chmod 755 backend/chroma_db
```
Check `CHROMA_PERSIST_DIR` in `.env`.

#### 3. `LiteLLM API Key Error`
**Cause**: Missing or invalid API key.
**Solution**:
- Verify `LITELLM_API_KEY` in `.env`.
- If using Ollama locally, ensure `OLLAMA_HOST` is correct and Ollama is running:
  ```bash
  ollama serve
  ```

#### 4. `Database Migration Errors`
**Cause**: Schema mismatch after updates.
**Solution**:
```bash
# Delete old DB (if development)
rm backend/narrative_nexus.db
# Restart server to recreate
uvicorn app.main:app --reload
```

#### 5. `Port 8000 already in use`
**Cause**: Another process holding the port.
**Solution**:
```bash
# Find process
lsof -i :8000
# Kill process (replace PID)
kill -9 <PID>
```

### Frontend Issues

#### 1. `npm install fails with ERESOLVE`
**Cause**: Dependency version conflicts.
**Solution**:
```bash
npm install --legacy-peer-deps
# OR clear cache
npm cache clean --force
npm install
```

#### 2. `Tailwind CSS styles not loading`
**Cause**: Incorrect PostCSS config or missing CSS import.
**Solution**:
- Ensure `src/index.css` contains:
  ```css
  @import "tailwindcss";
  ```
- Verify `postcss.config.js` uses `@tailwindcss/postcss`.
- Restart dev server: `npm run dev`.

#### 3. `API Connection Refused (Network Error)`
**Cause**: Backend not running or CORS misconfiguration.
**Solution**:
1. Verify backend is running on `http://localhost:8000`.
2. Check `VITE_API_URL` in `frontend/.env`.
3. Ensure backend `main.py` has CORS middleware:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:5173"],
       ...
   )
   ```

#### 4. `WebSocket Connection Failed`
**Cause**: Mismatched WS URL or server not supporting WS.
**Solution**:
- Check `VITE_WS_URL` in `frontend/.env` matches backend WS endpoint.
- Ensure backend `WebSocket` route is defined and active.

#### 5. `TypeScript Errors during build`
**Cause**: Type mismatches between API response and frontend types.
**Solution**:
- Run `npm run type-check` to see specific errors.
- Update `src/types/index.ts` to match backend Pydantic models.
- If using optional fields, ensure `?` is used in TypeScript interfaces.

### Docker Issues

#### 1. `Container exits immediately`
**Cause**: Missing environment variables or build errors.
**Solution**:
```bash
docker-compose logs <service-name>
# Fix .env or Dockerfile, then rebuild
docker-compose up --build
```

#### 2. `Volume Mount Permissions`
**Cause**: Host directory permissions prevent container write.
**Solution**:
```bash
chmod -R 777 backend/chroma_db
chmod -R 777 backend/data
```

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### End-to-End
Ensure both servers are running, then:
```bash
# Run E2E suite (if configured)
npm run e2e
```

---

## 📦 Deployment

### Docker Deployment
```bash
docker-compose up -d
```
Services available at:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`

### Production Checklist
- [ ] Set `DEBUG=false` in backend
- [ ] Use production database (PostgreSQL)
- [ ] Secure API keys in environment variables
- [ ] Enable HTTPS
- [ ] Configure reverse proxy (Nginx)
- [ ] Set up CI/CD pipelines

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- UI powered by [React](https://react.dev/) & [TailwindCSS](https://tailwindcss.com/)
- Vector search by [ChromaDB](https://www.trychroma.com/)
- State machine by [transitions](https://github.com/pytransitions/transitions)

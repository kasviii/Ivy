# 🌿 Ivy — Autonomous AI Research Agent

![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-green)
![LangGraph](https://img.shields.io/badge/LangGraph-agentic-purple)
![Groq](https://img.shields.io/badge/Groq-Llama3.3-orange)

Ivy is an autonomous AI research agent that performs **academic discovery, summarization, reflection, and literature synthesis** end-to-end with minimal human input.

Search papers → analyze findings → identify gaps → generate structured literature reviews.

---

## ✨ Features

- 🔍 Autonomous research pipeline
- 📚 Dual-source academic search (Arxiv + Semantic Scholar)
- 🧠 Reflection loop for gap analysis
- 📝 Structured literature review generation
- 📄 Export reviews as Markdown
- ⚡ Async job execution
- 🌙 Modern React UI with live status updates
- 🐳 Dockerized deployment
- 🔌 REST API with FastAPI

---

# 🏗️ Architecture

```text
User Input (Topic)
       │
       ▼
FastAPI Backend
       │
       ▼
LangGraph Agent
┌────────────────────────────────────┐
│ 1. Search                          │
│    → Arxiv + Semantic Scholar      │
│                                    │
│ 2. Summarize                       │
│    → Llama 3.3 70B via Groq        │
│                                    │
│ 3. Reflect                         │
│    → Gap Analysis + Critique       │
│                                    │
│ 4. Synthesize                      │
│    → Literature Review             │
└────────────────────────────────────┘
       │
       ▼
React Frontend
(Status + Export)
```

---

# 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| Agent Orchestration | LangGraph |
| LLM | Llama 3.3 70B (Groq) |
| Paper Search | Arxiv API + Semantic Scholar |
| Backend | FastAPI + Uvicorn |
| Frontend | React + Vite |
| Containerization | Docker Compose |
| Testing | Pytest |
| Language | Python 3.11 |

---

# 📁 Project Structure

```text
Ivy/
│
├── src/
│   ├── agent/
│   │   └── researcher.py
│   │
│   ├── api/
│   │   └── main.py
│   │
│   └── tools/
│       ├── arxiv_tool.py
│       └── semantic_tool.py
│
├── frontend/
│   └── src/
│       └── App.jsx
│
├── tests/
│   └── test_api.py
│
├── docker-compose.yml
├── dockerfile
├── dockerfile.frontend
├── requirements.txt
└── README.md
```

---

# 🚀 Quick Start

## Prerequisites

- Python 3.11
- Node.js 20+
- Docker Desktop
- Groq API Key

Create one at:

https://console.groq.com

---

## 1. Clone Repository

```bash
git clone https://github.com/kasviii/Ivy.git
cd Ivy
```

---

## 2. Configure Environment

```bash
cp .env.example .env
```

Add:

```env
GROQ_API_KEY=your_key_here
```

---

## 3. Run with Docker

```bash
docker-compose up --build
```

Open:

Frontend:
```
http://localhost:5173
```

API Docs:
```
http://localhost:8001/docs
```

---

## 4. Run Locally

### Backend

```bash
py -3.11 -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

uvicorn src.api.main:app --reload --port 8001
```

### Frontend

```bash
cd frontend

npm install

npm run dev
```

---

# 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API status |
| GET | `/health` | Health check |
| POST | `/research` | Start research job |
| GET | `/research/{job_id}` | Retrieve result |
| GET | `/research/{job_id}/status` | Poll status |
| GET | `/jobs` | List jobs |

---

# 🧠 Agent Workflow

```text
search_papers
      ↓
summarize_papers
      ↓
reflect
      ↓
synthesize
```

Conditional loop:

```text
reflect
   ↓
if gaps found
   ↓
search again
```

---

## Reflection Criteria

The agent evaluates:

- Coverage completeness
- Contradictions across papers
- Research diversity
- Sample sufficiency

If gaps exist and iteration count < 1:

```text
Search → Summarize → Reflect → Retry
```

---

# ⚙️ Model Configuration

| Task | Model | Temperature |
|------|------|------------|
| Summarization | Llama 3.3 70B | 0.3 |
| Reflection | Llama 3.3 70B | 0.3 |
| Synthesis | Llama 3.3 70B | 0.4 |

---

# 🧪 Testing

Run tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=src
```

---

# ⚠️ Limitations

- API rate limits may delay searches
- Jobs stored in memory only
- No authentication
- Groq free-tier token restrictions

---

# 🔮 Roadmap

- [ ] Redis job persistence
- [ ] WebSocket progress streaming
- [ ] PDF export
- [ ] Citation formatting (APA / MLA)
- [ ] Multi-language support
- [ ] User authentication

---

# 🤝 Contributing

Contributions are welcome.

```bash
fork → clone → branch → commit → PR
```

Example:

```bash
git checkout -b feature/new-feature
```

---

# 📜 License

MIT License

---

## ⭐ Support

If you found Ivy useful:

⭐ Star the repository  
🍴 Fork it  
🧠 Share feedback
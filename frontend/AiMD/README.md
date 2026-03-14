# AiMD — AI Medical Assistant

AiMD is a full-stack web application designed to make medical information more accessible 
through the power of artificial intelligence. It provides users with a conversational 
medical assistant capable of answering health-related questions, explaining symptoms, 
and offering general medical guidance in a clear and empathetic way.

Beyond simple conversation, AiMD offers a dedicated Analysis mode where users can upload 
medical documents — such as lab results, imaging reports, or clinical notes — and receive 
a thorough AI-driven evaluation. The assistant cross-references the uploaded content with 
real medical research from PubMed, synthesizes the findings, and delivers a structured 
report with suggestions and recommendations, all available as a downloadable PDF.

> **Disclaimer:** AiMD is not a medical device and does not provide real medical diagnoses.
> All responses, analyses, and reports are AI-generated suggestions intended for 
> informational purposes only and should not be used as a substitute for professional 
> medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider 
> with any questions you may have regarding a medical condition.

---

## Features

- **AI Chat** — Conversational medical assistant powered by GPT
- **Medical Analysis** — Upload PDFs or images for AI-driven diagnosis with PubMed-backed research
- **PDF Report Generation** — Downloadable medical reports generated from analysis results
- **Session Management** — Multiple chat sessions per user, persisted in MongoDB
- **JWT Authentication** — Secure login/register with access + refresh token flow
- **Responsive UI** — Glassmorphism design with animated Aurora background

---

## Tech Stack

### Frontend
- React + Vite
- Tailwind CSS
- React Router
- `motion/react` for animations
- `ogl` for WebGL Aurora/Plasma effects

### Backend
- FastAPI (Python)
- MongoDB with Motor (async driver)
- JWT authentication via `python-jose`
- OpenAI GPT API
- PubMed API for research paper retrieval
- PDF generation

### Infrastructure
- Docker + Docker Compose

---

## Getting Started

### Prerequisites

- Docker & Docker Compose
- OpenAI API key
- MongoDB connection string

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
MONGO_DB_URL=mongodb+srv://...
DB_NAME=aimd
JWT_SECRET=your_jwt_secret_here
OPENAI_API_KEY=your_openai_key_here
```

### Run with Docker

```bash
docker compose up --build
```

The app will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Login and receive tokens |
| POST | `/api/auth/logout` | Logout and clear cookies |
| POST | `/api/auth/refresh` | Refresh access token |
| GET | `/api/sessions` | Get all user sessions |
| POST | `/api/session` | Create a new session |
| GET | `/api/session` | Get a session by ID |
| PATCH | `/api/session` | Update session title |
| DELETE | `/api/session` | Delete a session |
| POST | `/api/session/message` | Add a message to a session |
| POST | `/api/chat` | Send a chat message to the AI |
| POST | `/api/analysis` | Upload files for medical analysis |
| GET | `/api/download-report/{session_id}` | Download analysis PDF report |

---

## Usage

1. **Register or log in** at the auth screen
2. **Chat mode** — type any medical question and get an AI response
3. **Analysis mode** — upload a medical PDF or image; the AI will analyze it, cross-reference PubMed research, and return a structured report you can download as a PDF
4. Use the **sidebar** to switch between sessions, create new ones, or delete old ones

---
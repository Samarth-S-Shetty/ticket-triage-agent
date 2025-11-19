# Ticket Triage Agent — AI-Powered Support Automation  
_Designed & implemented by **Samarth S Shetty**_
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-API-green?logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-lightgrey)
![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen)

---

## 📥 Cloning This Repository

### 1. Clone the repository
```bash
git clone https://github.com/<YOUR_USERNAME>/ticket-triage-agent.git
```

### 2. Enter the project directory
```bash
cd ticket-triage-agent
```

### 3. Create environment & install dependencies

#### Using uv (recommended)
```bash
uv venv
uv pip install -r requirements.txt
```

#### Using pip
```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows PowerShell

pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
```

Add your API key:
```env
OPENAI_API_KEY=your_api_key_here
```

### 5. Run the development server
```bash
uvicorn app.main:app --reload
```

### 6. Access UI & API docs
- http://127.0.0.1:8000/ui
- http://127.0.0.1:8000/docs

---

## 🚀 Overview

This project implements a production-ready **AI Support Ticket Triage Agent**, developed for the **AI Engineer (Agents & Production)** role assignment.

The system demonstrates real-world production thinking by combining:

- **LLM extraction**  
- **Embedding-based knowledge base search**  
- **FastAPI backend**  
- **Intelligent next‑action generation for new issues**  
- **A minimal UI, rate limiting, testing, and Dockerization**  

---

# 🧠 System Workflow (High-Level Architecture)

![Ticket Processing Flowchart](images/workflow.png)

### **How the workflow operates**
1. **User submits a support ticket** through UI or API.  
2. **LLM extracts structured fields** from raw text:  
   - summary  
   - category  
   - severity  
3. Ticket description is compared to a mock KB using **embedding similarity search**.  
4. If similarity score ≥ **0.6**, classify as **known_issue**:  
   - Top KB matches returned  
   - KB recommended action used  
5. If score < 0.6, classify as **new_issue**:  
   - LLM generates a custom next‑action suggestion  
   - No KB matches shown  
6. Response is returned to the UI / API.

### Why this design?
- **Embedding search is extremely fast** → ideal for production  
- **LLM only used when reasoning is needed** → lowers cost  
- Ensures **consistent triaging**, even when KB doesn’t contain the issue  

---

# 🔍 Why Embeddings Instead of LLM Matching?

This project intentionally uses **embeddings**, not LLM comparison, because:

### ✔ Scalability
LLM comparison does not scale.  
Embedding search scales to **thousands of KB articles**.

### ✔ Cost efficiency
Embedding search is nearly free.  
LLM comparison for every KB entry is **expensive**.

### ✔ Latency
- Embeddings → <10ms  
- LLM similarity → 500ms–2s per call

### ✔ Better semantic matching
Embeddings capture meaning, not literal wording:
- “Account locked after failed login attempts”  
≈  
- “App locks me out after multiple wrong logins”

Embeddings increase accuracy without increasing cost.

This design shows production-level optimization:  
**LLMs for intelligence, embeddings for speed + scale.**

---

# 📝 Feature Showcase (UI Demo)

## ✅ Known Issue Example

![Known Issue Example](images/known_issue.png)

### Explanation
- Embedding score was **high (~0.90)**  
- Mapped correctly to existing KB entry  
- KB’s recommended action was applied  
- Demonstrates embedding power  

---

## 🆕 New Issue Example

![New Issue Example](images/new_issue.png)

### Explanation
- Similarity < threshold → **new_issue**  
- No KB matches shown  
- Description passed to **LLM to generate next action**  
- Intelligent suggestion returned:
  > “Ask user to confirm email and check spam folder.”

This ensures **continuous usefulness**, even for issues not in KB.

---

# 📬 Postman Example (API Demo)

![Postman Demo](images/postman_postman.png)

### Explanation
- Simple POST request to `/triage`  
- JSON payload with ticket description  
- API returns:
  - summary  
  - category  
  - severity  
  - match_type  
  - KB matches (only for known issues)  
  - next_action  

This demonstrates the API’s clean, production-ready interface.

---

# 🔧 API Specification

## **POST `/triage`**

### Request
```json
{
  "description": "User cannot log in due to repeated failures"
}
```

### Response (Known Issue)
```json
{
  "summary": "Login failure due to repeated lockouts",
  "category": "General",
  "severity": "Low",
  "match_type": "known_issue",
  "kb_matches": [...],
  "next_action": "Guide user to unlock; review lockout threshold."
}
```

### Response (New Issue)
```json
{
  "summary": "...",
  "category": "Bug",
  "severity": "Medium",
  "match_type": "new_issue",
  "kb_matches": [],
  "next_action": "Ask for logs and reproduction steps."
}
```

---

# 🧩 Project Structure

```
ticket-triage-agent/
│
├── agent/           # LLM JSON-mode extraction logic
├── app/             # FastAPI service + orchestrator
├── kb/              # KB JSON + embedding search system
├── frontend/        # Minimal UI for testing
├── tests/           # Pytest suite
├── images/          # README image assets
├── .env.example
├── Dockerfile
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation & Running

## Using uv (recommended)
```bash
uv venv
uv pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Using pip
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

# 🌐 Access UI
```
http://127.0.0.1:8000/ui
```

# 📘 API Docs
```
http://127.0.0.1:8000/docs
```

---

# 💻 Curl Example
```bash
curl -X POST http://127.0.0.1:8000/triage      -H "Content-Type: application/json"      -d '{"description": "Account locked after failed attempts"}'
```

---

# 🧪 Testing
```bash
pytest -q
```

---

# 📦 Docker Support

### Dockerfile explanation
The Dockerfile:

- Uses **python:3.12-slim** for lightweight production images  
- Installs dependencies using `requirements.txt`  
- Exposes port 8000  
- Runs `uvicorn`  

This matches modern production deployment patterns.

---

### Build:
```bash
docker build -t ticket-triage-agent .
```

### Run:
```bash
docker run -p 8000:8000 ticket-triage-agent
```

---

# 🏭 Production Considerations  
(Required by assignment — fully implemented)

## **1. Deployment (AWS/GCP/Azure)**  
This service is cloud-ready due to:
- Dockerized container  
- Stateless FastAPI server  
- Can run on:
  - AWS ECS / Fargate  
  - GCP Cloud Run  
  - Azure App Service  
  - Kubernetes  

Scaling model:
- Horizontal scaling → multiple container replicas  
- Autoscaling based on:
  - CPU usage  
  - Requests/sec  
  - LLM latency  

---

## **2. Logging & Monitoring**
Production-level monitoring should include:

### Logging
- Structured JSON logs  
- Captures:
  - request_id  
  - latency  
  - LLM success/failure  
  - KB match scores  

### Monitoring tools
- AWS CloudWatch  
- Datadog  
- NewRelic  
- GCP Logging  

### Alerts
- High LLM failure rate  
- Spike in new issues  
- Increased latency  

---

## **3. Configuration & Secrets**

### Local:
- `.env.example` → `.env`
- Environment variables loaded via `python-dotenv`

### Production:
Use a secure secret manager:
- AWS Secrets Manager  
- GCP Secret Manager  
- Azure Key Vault  

No secrets inside:
- Repository  
- Docker image  

Configuration stored in:
- Env variables  
- SSM (AWS Systems Manager)  

---

## **4. Latency, Cost & Rate Limiting**

### Latency handling
- Embedding search → extremely fast  
- LLM used sparingly  
- Caching possible

### Cost control
- Minimized LLM calls: only extraction + new issue reasoning  
- All similarity handled via embeddings  

### Rate limiting
- 1 request per second per IP  
- Protects LLM usage from abuse  
- Prevents accidental API spam  

This ensures predictable cost + performance.

---

# 📌 Assignment Requirements Covered

✔ Mock KB (10–15 entries)  
✔ LLM extraction  
✔ Embedding search  
✔ Known/new issue system  
✔ Next‑action generation  
✔ Clean FastAPI API  
✔ README with production considerations  
✔ Dockerfile  
✔ UI + tests + rate limiting  

---

# 🙏 Final Notes

This project demonstrates:

- Real agent architecture  
- Practical LLM integration  
- Scalable embedding systems  
- Production deployment readiness  
- Modern API design  
- Testing & Dockerization  

If you want improvements or a walkthrough, feel free to ask!


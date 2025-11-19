
# Ticket Triage Agent — AI-Powered Support Automation  
_Designed & implemented by **Samarth S Shetty**_

---

## 🚀 Overview

This project implements a production-ready **AI Support Ticket Triage Agent**, developed as part of the **AI Engineer (Agents & Production)** role assignment.

The agent:

- Understands natural‑language ticket descriptions  
- Extracts summary, category, and severity using an LLM  
- Searches a mock **Knowledge Base (KB)** via embeddings  
- Classifies the ticket as **known_issue** or **new_issue**  
- Generates next actions  
- Exposes everything via a clean **FastAPI API**  
- Includes optional **web UI**, **pytest tests**, **rate limiting**, and **retry logic**  

---

# 🧠 System Workflow (High-Level Architecture)

Below is the core workflow of the system:

![Ticket Processing Flowchart](images/flowchart.png)

### **How the workflow operates**
1. **User submits a support ticket** from the UI or API.  
2. The raw text is sent to an **LLM**, which extracts key structured fields:  
   - summary  
   - category  
   - severity  

3. The ticket description is passed to the **embedding-based KB search**.  
4. If similarity score ≥ **0.6**, the ticket is marked **known_issue**.  
   - Return top KB matches  
   - Use recommended_action from KB  

5. Otherwise (score < 0.6), mark as **new_issue**:  
   - No KB matches returned  
   - Ticket description is sent to LLM for **next-action generation**  

6. Response is displayed in UI or returned via API.

This separation ensures:
- Fast + scalable KB lookup  
- Minimal LLM cost  
- Consistent triaging  

---

# 📝 Feature Showcase (UI Demo)

## ✅ Known Issue Example

When the user enters something *already in the KB*, the embedding model detects similarity:

![Known Issue Example](images/known_issue.png)

### **Explanation**
- Ticket matched KB entry **Account locked after failed login attempts**  
- LLM extracted:  
  - summary → good  
  - category → general  
  - severity → low  
- Match score was strong (0.90)  
- KB recommended action was returned  
- **This works because embeddings catch similar wording even if the phrasing changes**  

---

## 🆕 New Issue Example

If no KB result crosses the threshold:

![New Issue Example](images/new_issue.png)

### **Explanation**
- Ticket similarity < 0.6  
- No KB match  
- **Description sent to LLM** for custom next-action  
- User receives guidance such as:  
  > “Confirm email, ask user to check spam folder.”  

---

## 📬 Postman Example (API Demo)

POST request:

![Postman Demo](images/postman_postman.png)

---

# 🔧 API Specification

## **POST `/triage`**

### Request
```json
{
  "description": "User cannot log in due to repeated failures"
}
```

### Successful Response (Known Issue)
```json
{
  "summary": "...",
  "category": "General",
  "severity": "Low",
  "match_type": "known_issue",
  "kb_matches": [...],
  "next_action": "Guide user to unlock; review lockout threshold."
}
```

### Successful Response (New Issue)
```json
{
  "summary": "...",
  "category": "Bug",
  "severity": "Medium",
  "match_type": "new_issue",
  "kb_matches": [],
  "next_action": "Follow up for logs and request additional info."
}
```

---

# 🧩 Project Structure

```
ticket-triage-agent/
│
├── agent/           # LLM JSON-mode extraction logic
├── app/             # FastAPI service + orchestrator
├── kb/              # KB JSON + embedding search
├── frontend/        # Minimal test UI
├── tests/           # Pytest suite
├── images/          # README images
├── .env.example
├── Dockerfile
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation & Running

## **Using uv (recommended)**

```bash
uv venv
uv pip install -r requirements.txt
uvicorn app.main:app --reload
```

## **Using pip**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

# 🌐 Accessing UI

```
http://127.0.0.1:8000/ui
```

# 📘 API Docs (Swagger)

```
http://127.0.0.1:8000/docs
```

---

# 💻 Curl Example

### Known Issue Example
```bash
curl -X POST http://127.0.0.1:8000/triage      -H "Content-Type: application/json"      -d '{"description": "Account locked after failed attempts"}'
```

---

# 🧪 Testing

Run all tests:

```bash
pytest -q
```

---

# 📦 Docker Support

Included **Dockerfile** allows containerized deployment.

### Build image:
```bash
docker build -t ticket-triage-agent .
```

### Run container:
```bash
docker run -p 8000:8000 ticket-triage-agent
```

---

# 🏭 Production Considerations

### 🚀 Deployment Options
- AWS ECS / Fargate  
- GCP Cloud Run  
- Azure App Service  
- Docker + Kubernetes  

### 🧵 Configuration Handling
- `.env` file locally  
- Secret manager in production (AWS Secrets Manager, GCP Secret Manager)

### 🔐 Secrets
- Store API keys outside image  
- Inject via environment variables  

### 📊 Monitoring & Logging
- Structured JSON logs  
- CloudWatch / Stackdriver / Datadog  
- Request tracing  

### ⚡ Performance & Cost
- Minimal LLM usage → extraction + new-issue generation only  
- Embeddings scale cheaply to thousands of KB articles  
- In-memory rate limiting  

### 🔒 Rate Limiting
Simple per-IP throttle:

- 1 request per second  
- Prevents abuse & avoids unnecessary LLM cost  

---

# 📌 Assignment Assumptions

- Mock KB acceptable  
- No external datasets  
- Deterministic embedding search preferred over LLM search  
- UI optional but included  
- Safe JSON-mode LLM usage  

---

# 🙏 Final Notes

This project demonstrates:

- Agent design  
- LLM integration  
- Embedding search  
- FastAPI architecture  
- Production thinking  
- Dockerization  
- Testing discipline  

Feel free to ask for a walkthrough!


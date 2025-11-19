# Ticket Triage Agent — AI-Powered Support Automation  
_Designed & implemented by **Samarth S Shetty**_

---

## 🚀 Overview

This project implements a production-ready **AI Support Ticket Triage Agent**, developed as part of the **AI Engineer (Agents & Production)** role assignment.

The agent:

- Understands natural-language ticket descriptions  
- Extracts summary, category, and severity using an LLM  
- Searches a mock **Knowledge Base (KB)** via embeddings  
- Classifies the ticket as **known_issue** or **new_issue**  
- Generates next actions  
- Exposes everything via a clean **FastAPI API**  
- Includes optional **web UI**, **pytest tests**, **rate limiting**, and **retry logic**  

---

# 🧠 System Workflow (High-Level Architecture)

Below is the core workflow of the system:

![Ticket Processing Flowchart](images/workflow.png)

### **How the workflow operates**
1. **User submits a support ticket** from the UI or API.  
2. The raw text is sent to an **LLM**, which extracts key structured fields:  
   - summary  
   - category  
   - severity  

3. The ticket description is passed to the **embedding-based KB search**.  
4. If similarity score ≥ **0.6**, the ticket is marked **known_issue**:  
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

# 🔍 Why Embeddings Instead of LLM Matching?

This project intentionally uses **embedding-based similarity search**, not LLM-based similarity, because:

### ✔ **Embeddings are scalable**
- Can handle **thousands** of KB articles  
- Searching vectors is O(1) with indexing, unlike LLM calls (slow)

### ✔ **Embeddings are cheap**
LLM semantic similarity would require:
- Full prompt → reasoning → answer  
- $$$ at scale  
- High latency  
Embedding search costs **almost nothing** per query.

### ✔ **Embeddings capture semantic meaning**
Even with different phrasing:

> “Account locked after failed login attempts”  
vs  
> “Ongoing lockouts after repeated failed logins”  

➡ Both map to the same KB entry because embeddings capture **meaning**, not exact words.

### ✔ **LLM usage remains minimal & targeted**
Used only where reasoning matters:
- field extraction  
- next-action generation (new issues)

This matches real production systems:  
**LLMs for intelligence, embeddings for scalability.**

---

# 📝 Feature Showcase (UI Demo)

## ✅ Known Issue Example

![Known Issue Example](images/known_issue.png)

### **Explanation**
- Ticket matched KB entry **Account locked after failed login attempts**  
- LLM extracted fields correctly  
- Embedding score was strong (0.90)  
- KB recommended action was returned  
- Shows why embeddings outperform keyword matching  

---

## 🆕 New Issue Example

![New Issue Example](images/new_issue.png)

### **Explanation**
- Ticket similarity < 0.6  
- No KB result matched  
- System correctly identified **new_issue**  

### ✔ LLM Generates Next Action for New Issues
For new issues, the agent sends the user’s description directly to the LLM:

> Input: “Customer support is not responding to email.”

LLM returns a helpful next step:
> “Ask user to confirm the email address and check spam folder.”

This ensures **all tickets** receive intelligent, context-aware responses—even if not in the KB.

---

# 📬 Postman Example (API Demo)

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

### Build:
```bash
docker build -t ticket-triage-agent .
```

### Run:
```bash
docker run -p 8000:8000 ticket-triage-agent
```

---

# 🏭 Production Considerations (Assignment Requirement)

This section covers all four points explicitly mentioned in the assignment.

## **1. Deployment (AWS/GCP/Azure)**
A production deployment would use:

- **Docker container** (already included)
- Deployable on:
  - **AWS ECS / Fargate**
  - **GCP Cloud Run**
  - **Azure App Service**
- Stateless → horizontally scalable

Autoscaling based on:
- CPU usage  
- LLM latency  
- Requests/sec  

---

## **2. Logging & Monitoring**
Production logging would use:

- **Structured JSON logs**  
- Centralized logging:
  - AWS CloudWatch
  - GCP Logging (Stackdriver)
  - Elastic + Kibana  
  - Datadog / NewRelic

Monitoring:
- Request latency  
- LLM call failures  
- Similarity score anomalies  
- Rate-limit breaches  

---

## **3. Configuration & Secrets**
In development:
- `.env.example` → `.env`  
- API keys loaded using environment variables  

In production:
- Use **secret managers**:
  - AWS Secrets Manager  
  - GCP Secret Manager  
  - Azure Key Vault

Configuration stored in:
- Environment variables
- Parameter Store (SSM)  

---

## **4. Latency, Cost & Rate Limiting**
### **Latency**
- Embedding search → extremely fast (<10ms)  
- LLM calls minimized  
- Backend is fully async  

### **Cost Control**
- LLM used ONLY for:
  - Extraction  
  - New issue reasoning  
- KB embedding search is **almost free**  
- Rate limiter prevents abuse  

### **Rate Limiting**
- 1 request/sec per IP  
- Protects from:
  - Accidental refresh spam  
  - Malicious automated scripts  
  - Excessive LLM usage  

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

Feel free to ask for a walkthrough or improvements!

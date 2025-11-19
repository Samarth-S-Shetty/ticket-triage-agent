
# **Ticket Triage Agent (AI Engineer Take-Home Assignment)**  
_Designed & implemented by **Samarth S Shetty**_

---

##  **Overview**

This project implements an AI-powered **Support Ticket Triage Agent**, built as part of the take-home assignment for the **AI Engineer (Agents & Production)** role.

The goal is to design a realistic production-ready agent that:

- Understands free-text support tickets  
- Extracts key fields (summary, category, severity)  
- Searches a **mock knowledge base (KB)** of ~10–15 known issues  
- Determines if a ticket is a **known_issue** or **new_issue**  
- Suggests the **next action**  
- Exposes everything via a clean **FastAPI endpoint**  
- Includes a **minimal UI**, tests, rate-limiting & retry logic  

---

##  **What This Agent Does**

### **1) Understand the Ticket (LLM Extraction)**  
Given a user description like:

> “Checkout keeps failing with error 500 on mobile.”

The LLM extracts:

- `summary` → clear 1–2 line explanation  
- `category` → Bug / Login / Billing / Performance / Support / Other  
- `severity` → Low / Medium / High / Critical  

This logic is implemented in:  
`agent/llm_client.py`

LLM calls use `gpt-4.1-mini` with safe JSON mode + retries.

---

### **2) Knowledge Base Search (Embedding Approach)**

The agent loads a small KB (`kb/kb.json`) with 10–15 known issues.  
Each entry includes:

- id  
- title  
- symptoms  
- category  
- recommended_action  

#### **Why embeddings (vector similarity) instead of LLM matching?**
- Much cheaper  
- Scales to thousands of KB articles  
- Fast & deterministic  
- LLM similarity is expensive and slow at scale  
- Embeddings allow production-grade search (realtime latency)

This is implemented in:

`kb/search.py` → `search_kb(description)`

The agent returns the **top-3 KB matches** (only if known issue).

---

### **3) Known Issue vs New Issue Logic**

If the top KB score ≥ configurable threshold (default **0.6**):

- `match_type = "known_issue"`
- Include KB matches
- Use KB's recommended action

Otherwise:

- `match_type = "new_issue"`
- **No KB matches returned**
- Ticket description is sent to LLM to generate a **next action suggestion**  
  (e.g., "Ask user for reproduction steps and logs.")

This is implemented in:

`app/orchestrator.py`

---

### **4) Next Action Generation (LLM)**  
For **new issues**, the LLM proposes an actionable next step:

Examples:

- “Request more logs and escalate to backend team.”  
- “Ask user for screenshots and environment details.”  
- “Create an engineering ticket with repro details.”

This avoids generic fallback responses, adding real value.

---

##  **API Endpoint**

### **POST /triage**
Request:
```json
{
  "description": "I get a 500 error when checking out on mobile."
}
```

Response example (known issue):
```json
{
  "summary": "...",
  "category": "Bug",
  "severity": "High",
  "match_type": "known_issue",
  "kb_matches": [...],
  "next_action": "Escalate to payments team."
}
```

Response example (new issue):
```json
{
  "summary": "...",
  "category": "Support",
  "severity": "Medium",
  "match_type": "new_issue",
  "kb_matches": [],
  "next_action": "Ask user for logs and create an engineering ticket."
}
```

---

##  **Minimal Frontend (Optional)**
A small HTML UI (`frontend/index.html`) allows manual testing:

- Enter ticket description  
- View triage output  
- Demonstrates usability thinking  

---

##  **Project Structure**

```
ticket-triage-agent/
│
├── agent/           # LLM calls (OpenAI), JSON-mode extraction
├── app/             # FastAPI service, orchestrator, schemas
├── kb/              # KB JSON + embedding-based search
├── frontend/        # Minimal HTML UI
├── tests/           # pytest API tests
├── .env.example     # Environment config template
├── .gitignore
├── requirements.txt
└── README.md
```

---

##  **Tests Included**

Tests verify:

- API healthcheck  
- Triage endpoint shape  
- Known issue classification  
- New issue handling  
- Empty ticket rejection

Run tests:

```bash
pytest -q
```

---

##  **How to Run Locally**

### **1. Clone repo**
```bash
git clone https://github.com/<YOUR_USERNAME>/ticket-triage-agent.git
cd ticket-triage-agent
```

### **2. Create environment**
Using uv:

```bash
uv venv
uv pip install -r requirements.txt
```

Or classic pip:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### **3. Set up environment variables**
Copy the sample:

```bash
cp .env.example .env
```

Put your **OpenAI API key** in `.env`.

### **4. Start the server**
```bash
uvicorn app.main:app --reload
```

### **5. Open docs**
http://127.0.0.1:8000/docs

### **6. Optional UI**
http://127.0.0.1:8000/ui

---

##  **Production Considerations**

### **1. Deployment**
Ideal for:
- AWS ECS / Lambda / Fargate
- GCP Cloud Run  
- Azure App Service  
- Docker containers  

### **2. Scalability**
- Embedding-based KB search is scalable  
- LLM calls minimized (only essential extraction + next-action generation)  
- Fast response times suitable for production workloads  

### **3. Configurable**
Supports multiple envs:
- dev  
- staging  
- prod  

### **4. Reliability**
- LLM retries + backoff  
- JSON parsing safety  
- Rate limiting middleware  
- Error handling  

---

## **Assumptions (as per assignment)**

- Mock KB (10–15 entries) is acceptable  
- No external datasets required  
- LLM chosen freely  
- Simple UI is enough  
- Embeddings chosen because scalable + cheap  
- New ticket actions generated dynamically by LLM  

---

##  **Thank You**

This project demonstrates end‑to‑end understanding of:

- AI agents  
- FastAPI backend  
- LLM integration  
- Embedding search  
- Engineering design  
- Production readiness  

Feel free to reach out if you'd like a walkthrough or improvements!

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from app.schemas import TicketRequest, TicketResponse
from app.orchestrator import triage_ticket
import time

app = FastAPI(title="Ticket Triage Agent")

# -----------------------
# Rate Limiter Middleware
# -----------------------
RATE_LIMIT_STORE = {}   # ip -> last_request_time

@app.middleware("http")
async def rate_limiter(request: Request, call_next):
    ip = request.client.host
    now = time.time()

    last_time = RATE_LIMIT_STORE.get(ip, 0)

    # Allow only 1 request per second per IP
    if now - last_time < 1.0:
        raise HTTPException(status_code=429, detail="Too Many Requests, slow down.")

    RATE_LIMIT_STORE[ip] = now

    return await call_next(request)

# -----------------------
# Serve frontend
# -----------------------
app.mount("/ui", StaticFiles(directory="frontend", html=True), name="frontend")

# -----------------------
# Health Check
# -----------------------
@app.get("/")
def root():
    return {"message": "Triage agent running"}

# -----------------------
# Main Triage Endpoint
# -----------------------
@app.post("/triage", response_model=TicketResponse)
def triage(req: TicketRequest):
    if not req.description or not req.description.strip():
        raise HTTPException(status_code=400, detail="description is required")

    return triage_ticket(req.description)

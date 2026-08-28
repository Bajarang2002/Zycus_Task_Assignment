from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from triage import triage_ticket

app = FastAPI(
    title="Zycus Task 1 - Support Ticket Triage",
    version="1.0.0"
)

class TicketRequest(BaseModel):
    subject: str
    body: str
    product: str | None = None
    product_area: str | None = None
    plan_tier: str | None = None

@app.get("/")
def home():
    return {
        "message": "Zycus Task 1 API is running"
    }

@app.post("/triage")
def triage(request: TicketRequest):
    try:
        result = triage_ticket(
            subject=request.subject,
            body=request.body,
            product=request.product,
            product_area=request.product_area,
            plan_tier=request.plan_tier
        )
        return result

    except Exception as exc:
        print("TRIAGE ERROR:", exc)

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )
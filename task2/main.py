from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from health_summarizer import generate_health_brief

app=FastAPI(
    title="Zycus Task 2 - TAM Account Health Summarizer",
    version="1.0.0"
)

class AccountRequest(BaseModel):
    account_id:str

@app.get("/")
def home():
    return {
        "message":"Zycus Task 2 API is running",
        "endpoint":"POST /account-health"
    }

@app.post("/account-health")
def account_health(request:AccountRequest):
    account_id=request.account_id.strip()

    if not account_id:
        raise HTTPException(
            status_code=400,
            detail="account_id is required."
        )

    try:
        return generate_health_brief(account_id)

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
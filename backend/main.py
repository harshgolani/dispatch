import os
from fastapi import FastAPI, HTTPException, Request #type: ignore
from fastapi.middleware.cors import CORSMiddleware #type: ignore
from pydantic import BaseModel #type: ignore
from slowapi import Limiter, _rate_limit_exceeded_handler #type: ignore
from slowapi.util import get_remote_address #type: ignore
from slowapi.errors import RateLimitExceeded #type: ignore
from agent import run_agent

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Dispatch API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class ResearchRequest(BaseModel):
    company: str


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/research")
@limiter.limit("10/hour")
async def research(request: Request, body: ResearchRequest):
    if not body.company or len(body.company.strip()) == 0:
        raise HTTPException(status_code=400, detail="Company name is required")
    if len(body.company) > 100:
        raise HTTPException(status_code=400, detail="Company name too long")
    try:
        result = run_agent(body.company.strip())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

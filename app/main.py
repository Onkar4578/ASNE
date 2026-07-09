"""
ASNE - Adaptive Symbolic-Neural Engine
FastAPI entrypoint. Run with: uvicorn app.main:app --reload
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.core.router import handle_query

app = FastAPI(title="ASNE - Adaptive Symbolic-Neural Engine")

# Allow your React dashboard (running on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this before any real deployment
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str


@app.get("/")
def health_check():
    return {"status": "ASNE is running"}


@app.post("/query")
def query_endpoint(request: QueryRequest):
    """
    Main endpoint: send a query, get back an explainable response
    showing which layer handled it, confidence, latency, and cost.
    """
    result = handle_query(request.query)
    return result

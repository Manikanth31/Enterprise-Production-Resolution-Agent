from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.agents.agent import ResolutionAgent
from app.services.memory_store import AgentMemoryStore
from app.services.notification_service import AlertRouter


class InvestigationRequest(BaseModel):
    order_id: int
    incident_id: str


class AlertRequest(BaseModel):
    incident_id: str
    title: str
    message: str
    recipient: str | None = None


app = FastAPI(title="Enterprise Production Resolution Agent")
agent = ResolutionAgent()
memory_store = AgentMemoryStore()
alert_router = AlertRouter()


@app.get("/")
def root() -> dict:
    return {
        "status": "ok",
        "service": "enterprise-production-resolution-agent",
        "docs": "/docs",
        "health": "/health",
        "investigate": "/investigate?order_id=<order_id>&incident_id=<incident_id>",
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "enterprise-production-resolution-agent"}


@app.post("/investigate")
def investigate(request: InvestigationRequest) -> dict:
    try:
        return agent.run(order_id=request.order_id, incident_id=request.incident_id)
    except Exception as exc:  # pragma: no cover - API safety net
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/investigate")
def investigate_get(order_id: int, incident_id: str) -> dict:
    try:
        return agent.run(order_id=order_id, incident_id=incident_id)
    except Exception as exc:  # pragma: no cover - API safety net
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/memory")
def get_memory() -> dict:
    return {"items": memory_store.list_recent(limit=10), "summary": memory_store.get_summary()}


@app.post("/alert")
def send_alert(request: AlertRequest) -> dict:
    try:
        return alert_router.send_alert(request.incident_id, request.title, request.message, request.recipient)
    except Exception as exc:  # pragma: no cover - API safety net
        raise HTTPException(status_code=500, detail=str(exc)) from exc

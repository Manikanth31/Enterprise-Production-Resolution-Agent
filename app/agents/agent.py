from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import requests

from app.rag.knowledge_base import IncidentKnowledgeBase
from app.services.investigation_service import investigate
from app.services.memory_store import AgentMemoryStore


class ResolutionAgent:
    """Production incident resolution assistant."""

    def __init__(self, knowledge_base: Optional[IncidentKnowledgeBase] = None, memory_store: Optional[AgentMemoryStore] = None):
        self.knowledge_base = knowledge_base or IncidentKnowledgeBase()
        self.memory_store = memory_store or AgentMemoryStore()

    def run(self, order_id: int, incident_id: str) -> Dict[str, Any]:
        result = investigate(order_id=order_id, incident_id=incident_id)
        summary = self.summarize_result(result)
        memory_entry = self.memory_store.record_incident(
            incident_id=incident_id,
            order_id=order_id,
            summary=summary,
            rca=result["rca"].model_dump() if hasattr(result["rca"], "model_dump") else result["rca"].dict(),
        )

        return {
            "incident_id": incident_id,
            "order_id": order_id,
            "summary": summary,
            "rca": result["rca"].model_dump() if hasattr(result["rca"], "model_dump") else result["rca"].dict(),
            "evidence": result["evidence"],
            "memory": memory_entry,
        }

    def get_memory(self) -> list[dict[str, Any]]:
        return self.memory_store.list_recent(limit=10)

    def summarize_result(self, investigation_result: Dict[str, Any]) -> str:
        incident_id = investigation_result["incident_id"]
        order_id = investigation_result["order_id"]
        rca = investigation_result["rca"]

        incident = self.knowledge_base.load_incident(incident_id)
        incident_context = (
            f"Incident {incident_id}: {incident.get('title', 'No title available')}"
            f" | Severity: {incident.get('severity', 'UNKNOWN')}"
            f" | Status: {incident.get('status', 'UNKNOWN')}"
        )

        evidence_code = "UNKNOWN"
        if len(rca.evidence) > 1 and ': ' in rca.evidence[1]:
            evidence_code = rca.evidence[1].split(': ', 1)[1].rstrip('.')

        summary = (
            f"{incident_context}. "
            f"Order {order_id} was investigated and found to have {rca.root_cause} "
            f"with a severity of {rca.severity}. "
            f"Observed evidence includes the interface error code {evidence_code} "
            f"and recommended action: {rca.recommended_action}."
        )

        return self._maybe_enhance_summary(summary, investigation_result)

    def _maybe_enhance_summary(self, base_summary: str, investigation_result: Dict[str, Any]) -> str:
        prompt = (
            "You are a production incident response assistant. Rephrase the following incident summary in clear, confident operational language. "
            f"Keep the facts and avoid hallucinating. Summary: {base_summary}"
        )

        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if gemini_key:
            text = self._call_gemini(prompt, os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))
            if text:
                return text

        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            text = self._call_openai(prompt, os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
            if text:
                return text

        return base_summary

    def _call_gemini(self, prompt: str, model: str) -> str | None:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return None

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }

        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            candidates = data.get("candidates") or []
            if not candidates:
                return None
            parts = candidates[0].get("content", {}).get("parts") or []
            if not parts:
                return None
            text = parts[0].get("text")
            return text or None
        except Exception:
            return None

    def _call_openai(self, prompt: str, model: str) -> str | None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None

        try:
            from openai import OpenAI
        except ImportError:
            return None

        try:
            client = OpenAI(api_key=api_key)
            response = client.responses.create(
                model=model,
                input=prompt,
            )
            text = getattr(response, "output_text", None)
            if text:
                return text
        except Exception:
            return None

        return None

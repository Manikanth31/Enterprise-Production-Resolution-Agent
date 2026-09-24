from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


class AgentMemoryStore:
    """Persistent memory for previously investigated incidents."""

    def __init__(self, path: str | Path | None = None):
        base_dir = Path(__file__).resolve().parents[2]
        self.path = Path(path) if path is not None else base_dir / "data" / "agent_memory.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> List[Dict[str, Any]]:
        if not self.path.exists():
            return []

        try:
            with self.path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, list):
                return data
        except (json.JSONDecodeError, OSError):
            return []
        return []

    def _save(self, data: List[Dict[str, Any]]) -> None:
        with self.path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    def record_incident(self, incident_id: str, order_id: int, summary: str, rca: Dict[str, Any]) -> Dict[str, Any]:
        entries = self._load()
        event = {
            "incident_id": incident_id,
            "order_id": order_id,
            "summary": summary,
            "root_cause": rca.get("root_cause", "Unknown"),
            "severity": rca.get("severity", "UNKNOWN"),
            "confidence": rca.get("confidence", "UNKNOWN"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        entries.insert(0, event)
        self._save(entries[:50])
        return event

    def list_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self._load()[:limit]

    def get_summary(self) -> Dict[str, Any]:
        entries = self._load()
        if not entries:
            return {"total_incidents": 0, "recent_root_causes": [], "high_severity_count": 0}

        causes = {}
        for item in entries:
            key = item.get("root_cause", "Unknown")
            causes[key] = causes.get(key, 0) + 1

        return {
            "total_incidents": len(entries),
            "recent_root_causes": sorted(causes.items(), key=lambda x: x[1], reverse=True),
            "high_severity_count": sum(1 for item in entries if str(item.get("severity", "")).upper() in {"HIGH", "CRITICAL"}),
        }

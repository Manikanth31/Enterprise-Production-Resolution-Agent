from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


class IncidentKnowledgeBase:
    """Small retrieval layer for incident metadata and historical incident summaries."""

    def __init__(self, incidents_dir: Path | None = None):
        base_dir = Path(__file__).resolve().parents[2]
        self.incidents_dir = incidents_dir or base_dir / "data" / "incidents"

    def load_incident(self, incident_id: str) -> Dict[str, Any]:
        incident_path = self.incidents_dir / f"{incident_id}.json"
        if not incident_path.exists():
            return {
                "incident_id": incident_id,
                "title": "Unknown incident",
                "description": "No matching incident record was found.",
                "severity": "UNKNOWN",
                "status": "UNKNOWN",
            }

        with incident_path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def list_recent_incidents(self) -> List[Dict[str, Any]]:
        incidents: List[Dict[str, Any]] = []
        if not self.incidents_dir.exists():
            return incidents

        for incident_file in sorted(self.incidents_dir.glob("*.json")):
            with incident_file.open("r", encoding="utf-8") as fh:
                incidents.append(json.load(fh))
        return incidents

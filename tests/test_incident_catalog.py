from pathlib import Path

from app.rag.knowledge_base import IncidentKnowledgeBase


def test_demo_catalog_contains_multiple_incident_order_pairs():
    incidents = IncidentKnowledgeBase().list_recent_incidents()
    ids = {item["incident_id"] for item in incidents}

    assert len(ids) >= 7
    assert {"INC-1001", "INC-1002"}.issubset(ids)


def test_env_template_prefers_gemini_key():
    env_file = Path(__file__).resolve().parents[1] / ".env.example"
    content = env_file.read_text(encoding="utf-8")

    assert "GEMINI_API_KEY" in content
    assert "OPENAI_API_KEY" in content

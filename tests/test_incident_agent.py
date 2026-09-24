from app.services.investigation_service import investigate
from app.agents.agent import ResolutionAgent


def test_investigation_service_returns_expected_risk():
    result = investigate(order_id=5004, incident_id="INC-1001")

    assert result["incident_id"] == "INC-1001"
    assert result["order_id"] == 5004
    assert result["rca"].severity == "HIGH"
    assert "Downstream interface connection timeout" in result["rca"].root_cause


def test_resolution_agent_generates_summary():
    result = investigate(order_id=5004, incident_id="INC-1001")
    agent = ResolutionAgent()

    summary = agent.summarize_result(result)

    assert "INC-1001" in summary
    assert "5004" in summary
    assert "INT-500" in summary or "timeout" in summary.lower()

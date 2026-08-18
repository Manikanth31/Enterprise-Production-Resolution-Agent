from app.tools.incident_tool import investigate_incident
from app.tools.rca_tool import analyze_incident_evidence


def investigate(order_id: int, incident_id: str):
    """
    Run the complete incident investigation workflow.

    1. Collect database evidence.
    2. Analyze the evidence.
    3. Return the RCA result.
    """

    evidence = investigate_incident(order_id)

    rca_result = analyze_incident_evidence(
        incident_id,
        evidence
    )

    return {
        "incident_id": incident_id,
        "order_id": order_id,
        "evidence": evidence,
        "rca": rca_result
    }
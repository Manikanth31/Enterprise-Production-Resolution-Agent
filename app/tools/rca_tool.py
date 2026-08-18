from app.models.rca import RCAResult


def analyze_incident_evidence(
    incident_id: str,
    evidence: dict
) -> RCAResult:

    interface_data = evidence.get("interface", [])
    error_data = evidence.get("errors", [])

    if not interface_data:
        return RCAResult(
            incident_id=incident_id,
            root_cause="No interface transaction found.",
            evidence=[],
            severity="UNKNOWN",
            recommended_action="Investigate the order processing workflow.",
            confidence="LOW"
        )

    interface = interface_data[0]

    error_code = interface.get("error_code")
    error_message = interface.get("error_message")

    evidence_items = [
        f"Interface {interface['interface_id']} status is {interface['status']}.",
        f"Error code: {error_code}.",
        f"Error message: {error_message}."
    ]

    if error_data:
        error = error_data[0]

        evidence_items.append(
            f"Error log severity is {error['severity']}."
        )

        evidence_items.append(
            f"Error log message: {error['error_message']}."
        )

    if error_code == "INT-500":

        return RCAResult(
            incident_id=incident_id,
            root_cause="Downstream interface connection timeout.",
            evidence=evidence_items,
            severity="HIGH",
            recommended_action=(
                "Validate downstream interface connectivity "
                "and retry the failed transaction."
            ),
            confidence="HIGH"
        )

    if error_code == "DB-409":

        return RCAResult(
            incident_id=incident_id,
            root_cause="Duplicate transaction detected.",
            evidence=evidence_items,
            severity="CRITICAL",
            recommended_action=(
                "Investigate duplicate transaction handling "
                "before retrying the transaction."
            ),
            confidence="HIGH"
        )

    return RCAResult(
        incident_id=incident_id,
        root_cause="Unknown interface error.",
        evidence=evidence_items,
        severity="UNKNOWN",
        recommended_action="Perform further investigation.",
        confidence="LOW"
    )
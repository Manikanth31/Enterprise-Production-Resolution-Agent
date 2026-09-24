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

    if error_code in {"INT-500", "INT-503", "INT-504"}:

        return RCAResult(
            incident_id=incident_id,
            root_cause="Downstream interface connection timeout or latency issue.",
            evidence=evidence_items,
            severity="HIGH",
            recommended_action=(
                "Validate downstream interface connectivity, inspect timeout thresholds, "
                "and retry the failed transaction only after confirming the dependency is healthy."
            ),
            confidence="HIGH"
        )

    if error_code in {"DB-409", "DB-422"}:

        return RCAResult(
            incident_id=incident_id,
            root_cause="Duplicate transaction or retry conflict detected.",
            evidence=evidence_items,
            severity="CRITICAL",
            recommended_action=(
                "Investigate duplicate transaction handling and idempotency checks "
                "before retrying the transaction."
            ),
            confidence="HIGH"
        )

    if error_code in {"GATE-401", "GATE-403"}:
        return RCAResult(
            incident_id=incident_id,
            root_cause="Payment gateway authentication or authorization expired.",
            evidence=evidence_items,
            severity="HIGH",
            recommended_action=(
                "Refresh the gateway credentials or token, verify the payment integration configuration, "
                "and re-run the authorization request with a clean session."
            ),
            confidence="HIGH"
        )

    if error_code in {"INV-403", "INV-408", "INV-500"}:
        return RCAResult(
            incident_id=incident_id,
            root_cause="Inventory or reservation service rejected the request or timed out.",
            evidence=evidence_items,
            severity="MEDIUM",
            recommended_action=(
                "Check inventory service health and reservation policies, then retry the reservation "
                "after confirming stock and dependency availability."
            ),
            confidence="MEDIUM"
        )

    if error_code in {"WMS-429", "WMS-503", "WMS-504"}:
        return RCAResult(
            incident_id=incident_id,
            root_cause="Warehouse service throttling or temporary outage is blocking order fulfillment.",
            evidence=evidence_items,
            severity="HIGH",
            recommended_action=(
                "Reduce retry pressure on the warehouse API, confirm service capacity, and resume fulfillment "
                "after the downstream service stabilizes."
            ),
            confidence="HIGH"
        )

    return RCAResult(
        incident_id=incident_id,
        root_cause="Unknown interface error.",
        evidence=evidence_items,
        severity="UNKNOWN",
        recommended_action="Perform further investigation against the failing dependency and review the exact upstream error details.",
        confidence="LOW"
    )
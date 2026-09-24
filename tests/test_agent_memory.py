from app.services.memory_store import AgentMemoryStore


def test_memory_store_persists_incident_summary(tmp_path):
    store = AgentMemoryStore(path=tmp_path / "memory.json")

    store.record_incident(
        incident_id="INC-2001",
        order_id=5008,
        summary="Order 5008 failed due to interface timeout",
        rca={"severity": "HIGH", "root_cause": "interface timeout"},
    )

    entries = store.list_recent()
    assert len(entries) == 1
    assert entries[0]["incident_id"] == "INC-2001"
    assert entries[0]["order_id"] == 5008

from pydantic import BaseModel


class Incident(BaseModel):
    incident_id: str
    title: str
    description: str
    severity: str
    status: str
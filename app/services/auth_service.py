from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_USERS = {
    "admin": {"username": "admin", "password": "admin123", "role": "admin", "name": "System Administrator"},
    "operator": {"username": "operator", "password": "ops123", "role": "operator", "name": "Incident Operator"},
}


class AuthService:
    def __init__(self, path: str | Path | None = None):
        base_dir = Path(__file__).resolve().parents[2]
        self.path = Path(path) if path is not None else base_dir / "data" / "users.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_default_users()

    def _ensure_default_users(self) -> None:
        if self.path.exists():
            return
        payload = {username: {**data, "password": self.hash_password(data["password"])} for username, data in DEFAULT_USERS.items()}
        with self.path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)

    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        users = self._load()
        user = users.get(username)
        if not user:
            return None
        if user.get("password") == self.hash_password(password):
            return {"username": user["username"], "role": user["role"], "name": user["name"]}
        return None

    def _load(self) -> Dict[str, Any]:
        with self.path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def list_users(self) -> list[Dict[str, Any]]:
        return list(self._load().values())

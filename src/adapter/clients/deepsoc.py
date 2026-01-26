from __future__ import annotations
from typing import Any, Dict
import httpx

import requests
from adapter.config import settings
from adapter.clients.deepsoc_auth import DeepSOCAuth



def create_event(payload: dict) -> dict:
    token = DeepSOCAuth.get_token()
    url = f"{settings.deepsoc_base_url}/api/event/create"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    resp = requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=10
    )

    if resp.status_code != 200:
        raise RuntimeError(
            f"DeepSOC create event failed: {resp.status_code} {resp.text}"
        )

    return resp.json()


class DeepSOCClient:
    """DeepSOC API client.

    Default assumes:
      POST /api/event/create
    Adjust if your DeepSOC deployment differs.
    """

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.Client(timeout=5.0)

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"}

    def create_event(self, payload: Dict[str, Any], idempotency_key: str) -> Dict[str, Any]:
        headers = self._headers()
        headers["Idempotency-Key"] = idempotency_key
        r = self._client.post(f"{self.base_url}/api/event/create", json=payload, headers=headers)
        r.raise_for_status()
        return r.json()

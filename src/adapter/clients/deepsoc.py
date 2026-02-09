from __future__ import annotations

from typing import Any, Dict, Optional
import time
import httpx

from adapter.config import settings
from adapter.clients.deepsoc_auth import DeepSOCAuth


class DeepSOCClient:
    """
    DeepSOC API Client（唯一合法入口）

    职责：
    - 管理 JWT（自动获取 / 刷新）
    - 封装 HTTP 细节
    - 强制幂等（Idempotency-Key）
    """

    def __init__(
        self,
        base_url: Optional[str] = settings.deepsoc_base_url,
        timeout: float = 10.0,
    ):
        self.base_url = (base_url).rstrip("/")
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

    # =========================
    # 内部工具
    # =========================

    def _auth_header(self) -> Dict[str, str]:
        """
        获取 Authorization Header（自动刷新 token）
        """
        token = DeepSOCAuth.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _post(
        self,
        path: str,
        *,
        json: Dict[str, Any],
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        headers = self._auth_header()

        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        url = f"{self.base_url}{path}"

        resp = self._client.post(
            url,
            json=json,
            headers=headers,
        )

        # 统一异常语义
        if resp.status_code >= 400:
            raise RuntimeError(
                f"DeepSOC API error {resp.status_code}: {resp.text}"
            )

        return resp.json()

    # =========================
    # 对外 API
    # =========================

    def create_event(
        self,
        payload: Dict[str, Any],
        *,
        idempotency_key: str,
    ) -> Dict[str, Any]:
        """
        创建 DeepSOC 事件（强制幂等）

        :param payload: DeepSOC 事件 payload
        :param idempotency_key: 幂等 key（必须，通常用 fingerprint）
        """
        if not idempotency_key:
            raise ValueError("idempotency_key is required")
        print("create_event payload", payload)
        print("create_event idempotency_key", idempotency_key)
        return self._post(
            "/api/event/create",
            json=payload,
            idempotency_key=idempotency_key,
        )

    def get_token(self) -> str:
        """
        获取当前使用的 JWT token（只读）
        """
        return DeepSOCAuth.get_token()

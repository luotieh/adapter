from __future__ import annotations
from typing import Any, Dict, List
import httpx
from datetime import datetime, timezone

class FlowShadowClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.Client(timeout=8.0)

    def _headers(self) -> Dict[str, str]:
        # 你抓到的 cURL 没有鉴权头，所以这里默认不带 Authorization。
        # 如果你后面发现 ly_server 需要鉴权，再加回去。
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        # 可选：如果你确实有 token 才需要
        if self.api_key and self.api_key != "change-me":
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _parse_since_to_epoch(self, since: str) -> int:
        """
        since 可能是：
        - ISO8601: 2026-01-09T02:07:24.711640
        - epoch 秒字符串: 1767838800
        """
        s = (since or "").strip()
        if not s:
            return int(datetime.now(timezone.utc).timestamp()) - 600

        # epoch
        if s.isdigit():
            return int(s)

        # ISO8601（无时区时按 UTC 处理）
        try:
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return int(dt.timestamp())
        except Exception:
            # 解析失败就回看 10 分钟
            return int(datetime.now(timezone.utc).timestamp()) - 600

    def list_events(self, since: str, limit: int) -> List[Dict[str, Any]]:
        starttime = self._parse_since_to_epoch(since)
        endtime = int(datetime.now(timezone.utc).timestamp())

        # 关键：真实接口是 POST /d/event 且是 form-urlencoded
        form = {
            "req_type": "aggre",
            "starttime": str(starttime),
            "endtime": str(endtime),
        }

        r = self._client.post(
            f"{self.base_url}/d/event",
            data=form,
            headers=self._headers(),
        )
        r.raise_for_status()
        data = r.json()

        # 兼容多种返回格式：你可以按实际 JSON 再收敛
        if isinstance(data, list):
            return data[:limit]
        if isinstance(data, dict):
            # 常见字段尝试
            for k in ("items", "data", "rows", "list", "result"):
                v = data.get(k)
                if isinstance(v, list):
                    return v[:limit]
        return []

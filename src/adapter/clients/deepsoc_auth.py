import time
import requests
from adapter.config import settings


class DeepSOCAuth:
    _token: str | None = None
    _expires_at: float = 0

    @classmethod
    def get_token(cls) -> str:
        # token 未存在 或 已过期 → 登录
        if not cls._token or time.time() >= cls._expires_at:
            cls._login()
        return cls._token

    @classmethod
    def _login(cls):
        url = f"{settings.deepsoc_base_url}/api/auth/login"

        resp = requests.post(
            url,
            json={
                "username": settings.deepsoc_username,
                "password": settings.deepsoc_password,
            },
            timeout=10,
        )

        if resp.status_code != 200:
            raise RuntimeError(
                f"DeepSOC login failed: {resp.status_code} {resp.text}"
            )

        data = resp.json()

        token = data.get("access_token")
        if not token:
            raise RuntimeError("DeepSOC login response missing access_token")

        cls._token = token
        cls._expires_at = time.time() + settings.deepsoc_token_refresh_seconds

from __future__ import annotations

import httpx
from fastapi import APIRouter, HTTPException, Query

from adapter.config import settings
from adapter.logger import logger

router = APIRouter(tags=["sso"])


def _validate_sso_config() -> None:
    if not settings.iam_client_id or not settings.iam_client_secret:
        raise HTTPException(status_code=500, detail="IAM SSO 配置不完整：缺少 client_id/client_secret")
    if not settings.iam_redirect_uri:
        raise HTTPException(status_code=500, detail="IAM SSO 配置不完整：缺少 redirect_uri")


def _exchange_token(code: str) -> dict:
    token_url = f"{settings.iam_base_url.rstrip('/')}/auth/oauth2/token"

    try:
        resp = httpx.post(
            token_url,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": settings.iam_client_id,
                "client_secret": settings.iam_client_secret,
                "redirect_uri": settings.iam_redirect_uri,
            },
            timeout=10,
        )
    except httpx.HTTPError as exc:
        logger.exception("sso token exchange request failed")
        raise HTTPException(status_code=502, detail=f"调用 IAM token 端点失败: {exc}")

    if resp.status_code >= 400:
        logger.warning("sso token exchange failed: %s %s", resp.status_code, resp.text)
        raise HTTPException(status_code=502, detail=f"IAM token 交换失败: {resp.status_code}")

    try:
        return resp.json()
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=f"IAM token 响应非 JSON: {exc}")


def _get_userinfo(access_token: str) -> dict | None:
    if not access_token:
        return None

    userinfo_url = f"{settings.iam_base_url.rstrip('/')}/auth/oauth2/userinfo"

    try:
        resp = httpx.get(
            userinfo_url,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
    except httpx.HTTPError:
        logger.exception("sso userinfo request failed")
        return None

    if resp.status_code >= 400:
        logger.warning("sso userinfo failed: %s %s", resp.status_code, resp.text)
        return None

    try:
        return resp.json()
    except ValueError:
        return None


@router.get("/sso/callback")
def sso_callback(
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
):
    if not code:
        raise HTTPException(status_code=400, detail="缺少授权码 code")

    _validate_sso_config()

    token_data = _exchange_token(code)
    user_info = _get_userinfo(token_data.get("access_token", ""))

    return {
        "success": True,
        "state": state,
        "token_type": token_data.get("token_type"),
        "expires_in": token_data.get("expires_in"),
        "scope": token_data.get("scope"),
        "userinfo": user_info,
    }

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from ..deps import get_db, get_flowshadow_client, get_deepsoc_client
from ..config import settings
from ..services.sync import run_sync_once

router = APIRouter(prefix="/internal", tags=["internal-sync"])

def require_internal_key(x_api_key: str | None):
    if x_api_key != settings.adapter_internal_api_key:
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")

@router.post("/sync:run")
def sync_run(
    x_api_key: str | None = Header(default=None),
    db: Session = Depends(get_db),
    fs = Depends(get_flowshadow_client),
    ds = Depends(get_deepsoc_client),
):
    require_internal_key(x_api_key)
    return run_sync_once(
        db, fs, ds,
        batch_size=settings.sync_batch_size,
        lookback_seconds=settings.sync_lookback_seconds,
        max_retries=settings.sync_max_retries,
    )

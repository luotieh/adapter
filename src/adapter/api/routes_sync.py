from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from ..config import settings
from ..deps import get_db, get_flowshadow_client
from ..models import LyEvent
from ..services.pipeline import process_event

router = APIRouter(prefix="/internal", tags=["internal-sync"])


def require_internal_key(x_api_key: str | None):
    if x_api_key != settings.adapter_internal_api_key:
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")


@router.post("/sync:run")
def sync_run(
    x_api_key: str | None = Header(default=None),
    db: Session = Depends(get_db),
    fs = Depends(get_flowshadow_client),
):
    require_internal_key(x_api_key)

    # 1. 拉取流影事件（仍然是 raw dict）
    events = fs.list_events(
        limit=settings.sync_batch_size,
        lookback_seconds=settings.sync_lookback_seconds,
    )

    results = []

    # 2. 统一进入 pipeline
    for raw in events:
        event = LyEvent.model_validate(raw)
        result = process_event(
            db=db,
            event=event,
            source="sync"
        )
        results.append(result)

    return {
        "count": len(results),
        "results": results
    }

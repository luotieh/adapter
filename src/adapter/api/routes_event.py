from fastapi import APIRouter, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from ..config import settings
from ..deps import get_db, get_deepsoc_client
from ..services.pipeline import process_event
from ..logger import logger

router = APIRouter(prefix="/internal", tags=["internal-event"])

@router.post("/event/push")
def push_event(
    ly_event: dict,
    x_api_key: str | None = Header(default=None),
    db: Session = Depends(get_db),
    ds = Depends(get_deepsoc_client),
):
    if x_api_key != settings.adapter_internal_api_key:
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")

    try:
        return process_event(
            db=db,
            ly_event=ly_event,
            deepsoc_client=ds,
        )

    except ValueError as e:
        logger.warning("bad request", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        logger.exception("internal error in /event/push")
        raise HTTPException(
            status_code=500,
            detail="internal error, see server log",
        )

# adapter/api/routes_admin.py

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from adapter.config import settings
from adapter.deps import get_db
from adapter.models import EventMap
from adapter.logger import logger

router = APIRouter(
    prefix="/internal/admin",
    tags=["internal-admin"],
)

@router.post("/dedup/reset")
def reset_dedup(
    x_api_key: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    # 1. 内部鉴权
    if x_api_key != settings.adapter_internal_api_key:
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")

    # 2. 清空去重表
    deleted = db.query(EventMap).delete()
    db.commit()

    logger.warning(f"dedup table reset, deleted={deleted}")

    return {
        "success": True,
        "deleted_rows": deleted,
        "message": "dedup table cleared",
    }

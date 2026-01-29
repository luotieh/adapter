from fastapi import APIRouter, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from ..config import settings
from ..deps import get_db, get_deepsoc_client
from ..services.pipeline import process_event

router = APIRouter(prefix="/internal", tags=["internal-event"])

@router.post("/event/push")
def push_event(
    ly_event: dict,
    x_api_key: str | None = Header(default=None),
    db: Session = Depends(get_db),
    ds = Depends(get_deepsoc_client),
):
    # 1. 内部鉴权
    if x_api_key != settings.adapter_internal_api_key:
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")

    # 2. pipeline 处理（唯一入口）
    try:
        result = process_event(
            db=db,
            ly_event=ly_event,
            deepsoc_client=ds,
        )
        return result
    except ValueError as e:
        # 数据问题
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 系统 / 第三方问题
        raise HTTPException(status_code=500, detail=str(e))

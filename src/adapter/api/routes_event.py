from fastapi import APIRouter, Header, HTTPException
from adapter.config import settings
from adapter.models import LyEvent
from adapter.services.pipeline import process_event
from adapter.clients.deepsoc import create_event

router = APIRouter(prefix="/internal")


@router.post("/event/push")
def push_event(
    ly_event: dict,
    x_api_key: str = Header(None)
):
    if x_api_key != settings.adapter_internal_api_key:
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")

    try:
        payload = ly_event_to_deepsoc_payload(ly_event)
        result = create_event(payload)

        return {
            "success": True,
            "ly_event_id": ly_event.get("id"),
            "deepsoc_event_id": result.get("data", {}).get("event_id")
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "ly_event_id": ly_event.get("id"),
                "error": str(e)
            }
        )

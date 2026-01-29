from adapter.services.dedup import fingerprint, reserve, bind
from adapter.services.mapping import ly_event_to_deepsoc
from adapter.clients.deepsoc import create_event

from ..logger import logger

def process_event(db, ly_event: dict, deepsoc_client):
    try:
        logger.info("process_event start", extra={"ly_event": ly_event})

        fp = fingerprint(ly_event)

        if not reserve(db, fp):
            logger.info("duplicate event", extra={"fingerprint": fp})
            return {
                "skipped": True,
                "reason": "duplicate",
                "ly_event_id": ly_event.get("id"),
            }

        payload = ly_event_to_deepsoc(ly_event)
        logger.info("deepsoc payload ready", extra={"payload": payload})

        result = deepsoc_client.create_event(payload)
        logger.info("deepsoc create success", extra={"result": result})

        bind(
            db,
            fp,
            ly_id=ly_event.get("id"),
            deepsoc_id=result["data"]["event_id"],
        )

        return {
            "success": True,
            "ly_event_id": ly_event.get("id"),
            "deepsoc_event_id": result["data"]["event_id"],
        }

    except Exception:
        # ⭐ 关键：完整 traceback
        logger.exception("process_event failed")
        raise


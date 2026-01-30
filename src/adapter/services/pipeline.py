from adapter.services.dedup import fingerprint, reserve, bind
from adapter.services.mapping import ly_event_to_deepsoc
from adapter.clients.deepsoc import DeepSOCClient

from ..logger import logger

def process_event(db, ly_event: dict, deepsoc_client):
    try:
        logger.info("process_event start")

        fp = fingerprint(ly_event)

        ly_id=ly_event.get("id")

        if not reserve(db, fp):
            logger.info("event skipped (duplicate)")

            # duplicate 场景：允许获取一个“当前 token”
            token = deepsoc_client.get_token()

            return {
                "skipped": True,
                "reason": "duplicate",
                "fingerprint": fp,
                "ly_id": ly_id,
                "deepsoc_token": token,
            }

        payload = ly_event_to_deepsoc(ly_event)
        logger.info("deepsoc payload ready")

        token = deepsoc_client.get_token()
        
        result = deepsoc_client.create_event(
            payload=payload,
            idempotency_key=fp,
        )

        bind(
            db,
            fp,
            ly_id,
            deepsoc_id=result["data"]["event_id"],
        )

        logger.info("process_event success")

        return {
            "success": True,
            "fingerprint": fp,
            "ly_event_id": ly_event.get("id"),
            "deepsoc_event_id": result["data"]["event_id"],
            "deepsoc_token": token,
        }

    except Exception:
        # ⭐ 关键：完整 traceback
        logger.exception("process_event failed")
        raise


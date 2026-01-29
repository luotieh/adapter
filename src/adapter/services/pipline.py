from adapter.services.dedup import fingerprint, reserve, bind
from adapter.services.mapping import ly_event_to_deepsoc
from adapter.clients.deepsoc import create_event

def process_event(db, event, source: str):
    fp = fingerprint(event)

    if not reserve(db, fp):
        return {
            "skipped": True,
            "reason": "duplicate",
            "source": source,
        }

    payload = ly_event_to_deepsoc(event)
    result = create_event(payload)

    bind(
        db,
        fp,
        ly_id=event.id,
        deepsoc_id=result["data"]["event_id"],
    )

    return {
        "success": True,
        "source": source,
        "ly_event_id": event.id,
        "deepsoc_event_id": result["data"]["event_id"],
    }

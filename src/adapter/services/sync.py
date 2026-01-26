from __future__ import annotations
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models import SyncCursor, PushedEvent
from .mapping import make_idempotency_key, map_event_to_deepsoc

def get_or_create_cursor(db: Session, name: str = "flowshadow_events") -> SyncCursor:
    cur = db.query(SyncCursor).filter(SyncCursor.name == name).one_or_none()
    if cur:
        return cur
    cur = SyncCursor(name=name, last_ts="")
    db.add(cur)
    db.commit()
    db.refresh(cur)
    return cur

def already_pushed(db: Session, ly_event_id: str) -> bool:
    if not ly_event_id:
        return False
    return db.query(PushedEvent).filter(PushedEvent.ly_event_id == ly_event_id).one_or_none() is not None

def run_sync_once(db: Session, flowshadow, deepsoc, *,
                  batch_size: int, lookback_seconds: int, max_retries: int) -> dict:
    cursor = get_or_create_cursor(db)
    since = cursor.last_ts
    if not since:
        since = (datetime.utcnow() - timedelta(seconds=lookback_seconds)).isoformat()

    items = flowshadow.list_events(since=since, limit=batch_size)
    pushed = 0
    failed = 0
    newest_ts = since

    for ev in items:
        ly_event_id = str(ev.get("event_id") or "")
        ev_ts = str(ev.get("time") or "")
        if ev_ts and ev_ts > newest_ts:
            newest_ts = ev_ts

        # Prefer stable primary id; if missing, fall back to idem key as pseudo id
        idem_key = make_idempotency_key(ev)
        record_id = ly_event_id or f"noid:{idem_key}"

        if already_pushed(db, record_id):
            continue

        payload = map_event_to_deepsoc(ev)

        pe = PushedEvent(
            ly_event_id=record_id,
            idempotency_key=idem_key,
            status="FAILED",
            attempts=0,
        )
        db.add(pe)
        db.commit()

        ok = False
        last_err = ""
        for i in range(max_retries):
            try:
                pe.attempts = i + 1
                resp = deepsoc.create_event(payload, idempotency_key=idem_key)
                pe.deepsoc_event_id = str(resp.get("event_id") or resp.get("id") or "")
                pe.status = "SUCCESS"
                ok = True
                break
            except Exception as e:
                last_err = str(e)
                pe.last_error = last_err

        pe.updated_at = datetime.utcnow()
        db.commit()

        if ok:
            pushed += 1
        else:
            failed += 1

    cursor.last_ts = newest_ts
    cursor.updated_at = datetime.utcnow()
    db.commit()

    return {"since": since, "newest_ts": newest_ts, "fetched": len(items), "pushed": pushed, "failed": failed}

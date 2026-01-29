import hashlib
from sqlalchemy.orm import Session
from adapter.models import EventMap

def fingerprint(event) -> str:
    raw = f"{event.threat_source}|{event.victim_target}|{event.rule_desc}|{event.occurrence_time}"
    return hashlib.sha256(raw.encode()).hexdigest()

def reserve(db: Session, fp: str) -> bool:
    if db.get(EventMap, fp):
        return False

    db.add(EventMap(fingerprint=fp))
    db.commit()
    return True

def bind(db: Session, fp: str, ly_id: str, deepsoc_id: str):
    row = db.get(EventMap, fp)
    row.ly_event_id = ly_id
    row.deepsoc_event_id = deepsoc_id
    db.commit()

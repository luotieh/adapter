import hashlib
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from adapter.models import EventMap


def fingerprint(event: dict) -> str:
    raw = (
        f"{event.get('threat_source')}|"
        f"{event.get('victim_target')}|"
        f"{event.get('rule_desc')}|"
        f"{event.get('occurrence_time')}"
    )
    return hashlib.sha256(raw.encode()).hexdigest()


def reserve(db: Session, fp: str) -> bool:
    """
    预占指纹位（幂等 + 并发安全）
    """
    try:
        db.add(EventMap(fingerprint=fp))
        db.commit()
        return True
    except IntegrityError:
        db.rollback()
        return False


def bind(db: Session, fp: str, ly_id: str, deepsoc_id: str):
    row = db.get(EventMap, fp)
    if not row:
        return  # 安静失败，避免污染 pipeline

    row.ly_event_id = ly_id
    row.deepsoc_event_id = deepsoc_id
    db.commit()

def get_mapping(db: Session, fp: str) -> EventMap | None:
    return db.get(EventMap, fp)

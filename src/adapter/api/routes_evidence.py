from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session
from ..deps import get_db, get_flowshadow_client
from ..config import settings
from ..models import AuditLog

router = APIRouter(prefix="/internal", tags=["internal-evidence"])

def require_internal_key(x_api_key: str | None):
    if x_api_key != settings.adapter_internal_api_key:
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")

def audit(db: Session, actor: str, action: str, target: str, meta: str = ""):
    db.add(AuditLog(actor=actor, action=action, target=target, meta=meta))
    db.commit()

@router.get("/flows/{flow_id}")
def get_flow(
    flow_id: str,
    x_api_key: str | None = Header(default=None),
    x_actor: str | None = Header(default="deepsoc"),
    db: Session = Depends(get_db),
    fs = Depends(get_flowshadow_client),
):
    require_internal_key(x_api_key)
    data = fs.get_flow(flow_id)
    audit(db, x_actor or "deepsoc", "QUERY_FLOW", flow_id)
    return data

@router.get("/flows/{flow_id}/related")
def related(
    flow_id: str,
    window: str = Query("1h"),
    rel_type: str = Query("src"),
    limit: int = Query(50, ge=1, le=500),
    x_api_key: str | None = Header(default=None),
    x_actor: str | None = Header(default="deepsoc"),
    db: Session = Depends(get_db),
    fs = Depends(get_flowshadow_client),
):
    require_internal_key(x_api_key)
    data = fs.get_related_flows(flow_id, window=window, rel_type=rel_type, limit=limit)
    audit(db, x_actor or "deepsoc", "QUERY_RELATED", f"{flow_id}:{rel_type}:{window}:{limit}")
    return data

@router.get("/assets/{ip}")
def asset(
    ip: str,
    x_api_key: str | None = Header(default=None),
    x_actor: str | None = Header(default="deepsoc"),
    db: Session = Depends(get_db),
    fs = Depends(get_flowshadow_client),
):
    require_internal_key(x_api_key)
    data = fs.get_asset(ip)
    audit(db, x_actor or "deepsoc", "QUERY_ASSET", ip)
    return data

@router.post("/flows/{flow_id}/pcap:prepare")
def pcap_prepare(
    flow_id: str,
    x_api_key: str | None = Header(default=None),
    x_actor: str | None = Header(default="deepsoc"),
    db: Session = Depends(get_db),
    fs = Depends(get_flowshadow_client),
):
    require_internal_key(x_api_key)
    data = fs.prepare_pcap(flow_id)
    audit(db, x_actor or "deepsoc", "PREPARE_PCAP", flow_id)
    return data

@router.get("/pcaps/{pcap_id}")
def pcap_get(
    pcap_id: str,
    x_api_key: str | None = Header(default=None),
    x_actor: str | None = Header(default="deepsoc"),
    db: Session = Depends(get_db),
    fs = Depends(get_flowshadow_client),
):
    require_internal_key(x_api_key)
    data = fs.get_pcap(pcap_id)
    audit(db, x_actor or "deepsoc", "GET_PCAP", pcap_id)
    return data

from __future__ import annotations
from typing import Any, Dict
import hashlib
import json
from adapter.models import LyEvent


SEVERITY_MAP = {
    "极高": "high",
    "高": "high",
    "中": "medium",
    "低": "low"
}

def ly_event_to_deepsoc(ly_event: LyEvent) -> dict:
    """
    流影事件 → DeepSOC 事件创建 Payload
    """

    observables = [
        {
            "type": "ip",
            "value": ly_event.threat_source,
            "role": "source"
        },
        {
            "type": "ip",
            "value": ly_event.victim_target,
            "role": "destination"
        }
    ]

    context = {
        "ly_id": ly_event.id,
        "event_type": ly_event.event_type,
        "detail_type": ly_event.detail_type,
        "detection_method": ly_event.method,
        "occurrence_time": ly_event.occurrence_time,
        "duration": ly_event.duration,
        "is_active": ly_event.is_active,
        "processing_status": ly_event.processing_status,
        "system_ref": "FlowShadow"
    }

    return {
        "title": f"{ly_event.rule_desc} ({ly_event.event_type})",
        "message": (
            f"SIEM告警：检测到 {ly_event.threat_source} "
            f"对 {ly_event.victim_target} 发起 "
            f"{ly_event.rule_desc} 攻击，"
            f"检测方式：{ly_event.method}"
        ),
        "severity": SEVERITY_MAP.get(
            ly_event.event_level,
            "medium"
        ),
        "source": "FlowShadow",
        "category": "Network Threat",
        "context": json.dumps(context, ensure_ascii=False),
        "observables": observables
    }

def make_idempotency_key(ly_event: Dict[str, Any]) -> str:
    ly_event_id = str(ly_event.get("event_id") or "")
    if ly_event_id:
        return hashlib.sha256(ly_event_id.encode("utf-8")).hexdigest()[:32]

    raw = "|".join([
        str(ly_event.get("probe_id","")),
        str(ly_event.get("analyser_id","")),
        str(ly_event.get("threat_type","")),
        str(ly_event.get("flow_id","")),
        str(ly_event.get("time","")),
    ])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]

def map_event_to_deepsoc(ly_event: Dict[str, Any]) -> Dict[str, Any]:
    src_ip = ly_event.get("src_ip")
    dst_ip = ly_event.get("dst_ip")
    proto = ly_event.get("protocol")
    dport = ly_event.get("dst_port")
    threat = ly_event.get("threat_type", "UnknownThreat")
    sev = ly_event.get("severity", "medium")
    conf = ly_event.get("confidence")

    title = f"{threat}: {src_ip} → {dst_ip} ({proto}/{dport})"

    payload: Dict[str, Any] = {
        "title": title,
        "severity": sev,
        "category": "Network Threat",
        "source": "FlowShadow",
        "message": ly_event.get("message") or "",
        "context": {
            "external_ref": {
                "system": "flowshadow",
                "ly_event_id": ly_event.get("event_id"),
                "flow_id": ly_event.get("flow_id"),
                "probe_id": ly_event.get("probe_id"),
                "analyser_id": ly_event.get("analyser_id"),
            },
            "confidence": conf,
            "time": ly_event.get("time"),
        },
        "observables": [],
    }

    if src_ip:
        payload["observables"].append({"type": "ip", "value": src_ip, "role": "source"})
    if dst_ip:
        payload["observables"].append({"type": "ip", "value": dst_ip, "role": "destination"})
    if proto:
        payload["observables"].append({"type": "protocol", "value": proto})
    if dport is not None:
        payload["observables"].append({"type": "port", "value": dport})

    return payload

from adapter.services.dedup import fingerprint, reserve, bind
from adapter.services.mapping import ly_event_to_deepsoc
from adapter.clients.deepsoc import create_event

def process_event(
    *,
    db,
    ly_event: dict,
    deepsoc_client,
):
    """
    pipeline 唯一入口
    ly_event: 来自 API / sync 的原始 dict
    """

    # 1. 基础校验（兜底）
    ly_id = ly_event.get("id")
    if not ly_id:
        raise ValueError("ly_event.id is required")

    # 2. 指纹 & 去重
    fp = fingerprint(ly_event)

    if not reserve(db, fp):
        return {
            "skipped": True,
            "reason": "duplicate",
            "ly_event_id": ly_id,
        }

    # 3. 映射为 DeepSOC payload
    payload = ly_event_to_deepsoc(ly_event)

    # 4. 调用 DeepSOC
    result = deepsoc_client.create_event(payload)

    deepsoc_id = (
        result.get("data", {}) or {}
    ).get("event_id")

    if not deepsoc_id:
        raise RuntimeError(f"invalid deepsoc response: {result}")

    # 5. 绑定关系
    bind(
        db,
        fp,
        ly_id=ly_id,
        deepsoc_id=deepsoc_id,
    )

    return {
        "success": True,
        "ly_event_id": ly_id,
        "deepsoc_event_id": deepsoc_id,
    }


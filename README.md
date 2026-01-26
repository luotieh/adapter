# ly-deepsoc-adapter

用于将 FlowShadow（ly_probe / ly_analyser / ly_server）与 DeepSOC 融合的适配器服务（Python）。

## 功能
- **事件同步**（Pull -> Push）：从 `ly_server` 拉取新威胁事件，映射后推送到 DeepSOC。
- **证据回查 API**：提供 flow / related / asset / pcap 等查询接口，供 DeepSOC 事件详情页与 AI 工具调用。
- **工程化保障**：幂等去重、重试、审计日志、缓存（可扩展）。

## 运行要求
- Python 3.10+
- 网络可访问 `ly_server` 与 DeepSOC
- （可选）将 SQLite 换成 MySQL：改 `DATABASE_URL`

## 快速开始
```bash
cp .env.example .env
# 修改 .env 里的地址与 key
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
uvicorn adapter.main:app --host 0.0.0.0 --port 9010
```

健康检查：
```bash
curl http://localhost:9010/healthz
```

回查（由 DeepSOC 后端调用，需 internal key）：
```bash
curl -H "X-API-Key: <ADAPTER_INTERNAL_API_KEY>" \
  http://localhost:9010/internal/flows/<flow_id>
```

手动触发同步：
```bash
curl -X POST -H "X-API-Key: <ADAPTER_INTERNAL_API_KEY>" \
  http://localhost:9010/internal/sync:run
```

## 重要：需要你对接的真实 API
本项目默认在 `src/adapter/clients/flowshadow.py` 使用占位路径：
- `GET  {FLOWSHADOW_BASE_URL}/d/events`
- `GET  {FLOWSHADOW_BASE_URL}/d/flows/{flow_id}`
- `GET  {FLOWSHADOW_BASE_URL}/d/flows/{flow_id}/related`
- `GET  {FLOWSHADOW_BASE_URL}/d/assets/{ip}`
- `POST {FLOWSHADOW_BASE_URL}/d/flows/{flow_id}/pcap:prepare`
- `GET  {FLOWSHADOW_BASE_URL}/d/pcaps/{pcap_id}`

你需要按 `ly_server` 的实际接口（或你新增的网关接口）替换这些路径/参数/认证方式。

DeepSOC 事件创建接口默认：
- `POST {DEEPSOC_BASE_URL}/api/event/create`

如果 DeepSOC 的路径/鉴权不同，改 `src/adapter/clients/deepsoc.py` 即可。

## 安全建议
- `/internal/*` 仅允许 DeepSOC 后端所在内网访问
- 使用 `ADAPTER_INTERNAL_API_KEY` 并开启审计
- PCAP 建议采用临时签名 URL 或代理下载

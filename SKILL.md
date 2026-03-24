---
name: ops-memos-rollout
description: Deploy, repair, and verify MemOS memory server on macOS for OpenClaw. Use when setting up MemOS from scratch, troubleshooting MemOS add/search failures, onboarding Mac minis as clients to a shared MemOS server, or diagnosing empty search results. Triggers on "MemOS", "memos server", "memory server", "memos deploy", "memos search empty", "memos not working".
---

# MemOS Rollout

## Architecture

MemOS is a REST API memory service (Docker: neo4j + qdrant + API server) providing structured long-term memory with auto-extraction of facts, preferences, and skills from conversations.

- Default port: **8765**
- Docker socket (macOS): `unix:///Users/scott/.colima/default/docker.sock`
- Provider: SiliconFlow (Qwen2.5-72B LLM + bge-m3 embedding)

## ⚠️ Critical: API Format

The #1 failure mode is wrong write format. **`/product/add` requires chat message array, NOT plain text.**

### Correct write format

```json
{
  "user_id": "openclaw",
  "session_id": "session-001",
  "async_mode": "sync",
  "messages": [
    {"role": "user", "content": "Memory content here"},
    {"role": "assistant", "content": "Acknowledged."}
  ]
}
```

### Wrong formats (silent failure — 200 but nothing stored)

- `{"text": "content"}` — field does not exist in API schema
- `{"messages": "string content"}` — string messages not supported

### Search format

```json
{"query": "search terms", "user_id": "openclaw"}
```

`user_id` is **required** for both add and search.

## Deploy New Server

```bash
bash scripts/memos_server_up.sh
```

Starts 3 containers: `memos-neo4j`, `memos-qdrant`, `memos-api`. Reads config from `~/.openclaw/services/memos-server/.env`.

If `.env` doesn't exist, generate it from Cognee's SiliconFlow config:

```bash
python3 scripts/configure_memos_server.py
```

## Verify

```bash
python3 scripts/memos_client_smoke_test.py --base-url http://127.0.0.1:8765 --user-id test
```

Performs real add+search cycle. Success = memory written AND recalled.

## Health Check

No `/health` endpoint. Use `/docs` (Swagger UI) or real business endpoints.

## Onboard Client Mac Mini

```bash
bash scripts/onboard_memos_client.sh --base-url http://SERVER_IP:8765 --user-id CLIENT_ID
```

## Install Autostart

```bash
bash scripts/install_memos_launchagent.sh
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Add 200 but search empty | Wrong write format (`text` field) | Use `messages` array with `{role, content}` objects |
| Add 200 but search empty | Missing `user_id` in search | Add `user_id` to search payload |
| `/health` returns 404 | No health route in this API version | Use `/docs` or business endpoints |
| Container won't start | Colima not running | `colima start` first |
| Embedding fails | SiliconFlow token invalid | Check `.env` `EMBEDDING_API_KEY` |

## Known issues (2026-03-24)

### neo4j write bottleneck under sustained load

**Symptom:** `/product/add` returns 200 for ~40 consecutive writes, then starts timing out (10s+). Search remains stable.

**Root cause:** `add_nodes_batch` in neo4j blocks during graph node creation. Under sustained write pressure, the graph computation queue backs up.

**Impact:** Normal usage is fine (writes are sparse). Only affects burst scenarios like batch imports or stress tests.

**Mitigation:**
- Increase timeout if doing batch imports
- Batch multiple facts into a single `messages` array rather than one-per-call
- If neo4j hangs completely: `docker restart memos-api`

### SimpleStruct MemReader warning

**Symptom:** Logs show `SimpleStruct MemReader does not support str message data now, your messages contains [None], skipping`

**Root cause:** Some `/product/add` calls pass content as plain string instead of chat message array. The API returns 200 but nothing is actually stored.

**Fix:** Always use the correct message format (see "Critical: API Format" above).

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/configure_memos_server.py` | Generate .env from Cognee SiliconFlow config |
| `scripts/memos_server_up.sh` | Start Docker containers |
| `scripts/memos_server_status.sh` | Check container status |
| `scripts/memos_server_down.sh` | Stop containers |
| `scripts/install_memos_launchagent.sh` | macOS autostart |
| `scripts/memos_client_smoke_test.py` | Real add+search validation |
| `scripts/onboard_memos_client.sh` | One-command client onboard |

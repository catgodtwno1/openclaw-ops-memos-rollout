# MemOS API Format Reference

## /product/add — Full Schema

Key fields from OpenAPI spec (`APIADDRequest`):

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `user_id` | string | No (but needed for search) | Logical user / cube id |
| `session_id` | string | No | Groups related memories |
| `messages` | array of chat messages | No | **Must be array, not string** |
| `async_mode` | "sync" \| "async" | No | Default "async"; use "sync" for immediate |
| `task_id` | string | No | Task context |
| `manager_user_id` | string | No | Manager context |
| `project_id` | string | No | Project context |
| `mode` | string | No | Processing mode |
| `custom_tags` | object | No | Custom metadata |
| `info` | string | No | Additional info |
| `chat_history` | array | No | Historical context |
| `is_feedback` | boolean | No | Mark as feedback |
| `mem_cube_id` | string | No | Target memory cube |
| `memory_content` | string | No | Direct memory content |
| `doc_path` | string | No | Document path |
| `source` | string | No | Source identifier |
| `operation` | string | No | Operation type |

### Message formats supported

```json
// Chat completion messages (RECOMMENDED)
{"role": "user", "content": "text"}
{"role": "assistant", "content": "text"}
{"role": "system", "content": "text"}

// Content part arrays
[{"type": "text", "text": "content"}]

// File objects
{"filename": "doc.pdf", "content": "base64..."}
```

### NOT supported

```json
// Plain string — causes "does not support str message data"
"messages": "plain text string"
```

## /product/search — Response Structure

```json
{
  "code": 200,
  "data": {
    "text_mem": [{"cube_id": "...", "memories": [...]}],
    "act_mem": [],
    "para_mem": [],
    "pref_mem": [{"cube_id": "...", "memories": [], "total_nodes": 0}],
    "pref_note": "",
    "tool_mem": [{"cube_id": "...", "memories": []}],
    "skill_mem": [{"cube_id": "...", "memories": []}]
  }
}
```

Each memory object contains:
- `id`: UUID
- `memory`: Extracted text (auto-summarized by MemOS)
- `metadata.type`: "fact" | "preference" | "skill" | etc.
- `metadata.confidence`: 0.0–1.0
- `metadata.tags`: auto-generated array
- `metadata.background`: contextual explanation
- `metadata.relativity`: search relevance score
- `ref_id`: short reference ID

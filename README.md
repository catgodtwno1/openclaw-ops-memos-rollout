# ops-memos-rollout

MemOS 記憶伺服器的部署、修復與驗證技能，適用於 OpenClaw 五層記憶棧的 L3.5 層。

## 功能

- **一鍵部署** — Docker 容器自動啟動（Neo4j + Qdrant + API Server）
- **客戶端接入** — 將多台 Mac mini 連接到同一 MemOS 伺服器
- **故障診斷** — 覆蓋常見問題：寫入超時、搜索為空、Neo4j 瓶頸
- **NAS 部署** — 支援 QNAP/Synology NAS 上的 Docker 部署（含持久化策略）

## 適用場景

- 從零搭建 MemOS 記憶伺服器
- 排查 `/product/add` 超時或 `/product/search` 返回空結果
- 將新機器作為客戶端接入已有 MemOS 伺服器
- 在 NAS 上部署 MemOS（QNAP Container Station / Synology Docker）

## 核心知識

### API 格式（最常見的坑）

寫入必須用 chat message 陣列格式，不是純文字：

```json
{
  "user_id": "openclaw",
  "session_id": "session-001",
  "messages": [
    {"role": "user", "content": "要記住的內容"},
    {"role": "assistant", "content": "已記錄。"}
  ]
}
```

### 已修復的已知問題

| 問題 | 根因 | 修復方案 |
|------|------|----------|
| 連續寫入 ~130 次後超時 | Neo4j 缺少索引，全表掃描 O(N) | 創建複合索引 + RANGE 索引 |
| NAS 上每次寫入 7-15 秒 | `ASYNC_MODE=sync` → fine mode → 調 LLM | Patch core.py 強制 fast mode |
| 容器間 DNS 解析失敗 | 預設 bridge 網路不支援容器名 DNS | 使用自訂 Docker network `oc-memory` |
| Patch 重啟後遺失 | Docker 容器檔案系統為暫存 | Bind mount + docker commit 雙保險 |

## 目錄結構

```
SKILL.md              # 完整操作手冊（部署、驗證、排障）
scripts/
  configure_memos_server.py     # 從 Cognee 配置生成 .env
  memos_server_up.sh            # 啟動 Docker 容器
  memos_server_status.sh        # 檢查容器狀態
  memos_server_down.sh          # 停止容器
  install_memos_launchagent.sh  # macOS 開機自啟
  memos_client_smoke_test.py    # 寫入+搜索驗證
  onboard_memos_client.sh       # 一鍵客戶端接入
```

## 安裝

將此目錄放到 `~/.openclaw/workspace/skills/` 下，OpenClaw 會自動載入。

## 授權

MIT

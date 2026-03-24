#!/bin/zsh
set -euo pipefail

export DOCKER_HOST="unix:///Users/scott/.colima/default/docker.sock"

echo '=== containers ==='
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | egrep 'memos-(api|neo4j|qdrant)|NAMES' || true

echo '\n=== readiness ==='
curl -fsS http://127.0.0.1:8765/docs >/dev/null && echo 'MemOS API docs reachable: OK' || echo 'MemOS API not reachable'

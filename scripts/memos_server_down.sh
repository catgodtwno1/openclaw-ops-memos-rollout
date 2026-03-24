#!/bin/zsh
set -euo pipefail

export DOCKER_HOST="unix:///Users/scott/.colima/default/docker.sock"

docker rm -f memos-api memos-neo4j memos-qdrant >/dev/null 2>&1 || true
echo 'MemOS containers stopped.'

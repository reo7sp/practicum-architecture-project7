#!/bin/bash
set -e

[ -d /app/download ] && rm -rf /app/download
git clone --depth 1 --branch "$REPO_BRANCH" "$REPO_URL" /app/download

mkdir -p /data/logs
export KNOWLEDGE_BASE_DIR=/app/download/$REPO_KNOWLEDGE_BASE_DIR
export CHROMA_DB_DIR=/data/chroma_db
export INDEX_UPDATE_LOG=/data/logs/index_update.log
/app/.venv/bin/python /app/build_index.py

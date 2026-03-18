#!/bin/bash
set -e

echo "$CRON_SCHEDULE root /app/update.sh >> /data/logs/cron.log 2>&1" > /etc/cron.d/index-update
chmod 0644 /etc/cron.d/index-update
mkdir -p /data/chroma_db /data/logs

exec cron -f

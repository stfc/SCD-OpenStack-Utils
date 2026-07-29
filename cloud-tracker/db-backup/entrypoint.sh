#!/bin/bash
set -e

SCHEDULE="${BACKUP_SCHEDULE:-0 2 * * *}"

echo "Installing cron schedule: ${SCHEDULE}"

# Write crontab
echo "${SCHEDULE} /usr/local/bin/backup.sh >> /var/log/backup.log 2>&1" | crontab -

# Run an immediate backup on first start
echo "Running initial backup..."
/usr/local/bin/backup.sh

# Start crond in foreground
echo "Starting crond..."
crond -f -l 8

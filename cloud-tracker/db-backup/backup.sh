#!/bin/bash
set -e

BACKUP_DIR="/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="${BACKUP_DIR}/cloudtracker_${TIMESTAMP}.sql.gz"
RETAIN_DAYS="${BACKUP_RETAIN_DAYS:-7}"

echo "[$(date -u)] Starting backup..."

pg_dump \
    --host="${PGHOST}" \
    --username="${PGUSER}" \
    --dbname="${PGDATABASE}" \
    --format=plain \
    --no-password \
    | gzip > "${FILENAME}"

SIZE=$(du -sh "${FILENAME}" | cut -f1)
echo "[$(date -u)] Backup complete: ${FILENAME} (${SIZE})"

# Remove backups older than RETAIN_DAYS
find "${BACKUP_DIR}" -name "cloudtracker_*.sql.gz" -mtime "+${RETAIN_DAYS}" -delete
echo "[$(date -u)] Pruned backups older than ${RETAIN_DAYS} days"

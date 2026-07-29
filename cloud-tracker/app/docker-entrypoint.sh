#!/bin/bash
set -e

# If real certs were mounted, ensure permissions are correct
if [ -f /etc/ssl/cloudtracker/server.crt ] && [ -f /etc/ssl/cloudtracker/server.key ]; then
    chmod 600 /etc/ssl/cloudtracker/server.key
    chmod 644 /etc/ssl/cloudtracker/server.crt
fi

# Wait for database to be ready
echo "Waiting for database..."
until python3 -c "
import os, sys, psycopg2
try:
    psycopg2.connect(os.environ['DATABASE_URL'])
    print('Database ready.')
except Exception as e:
    print(f'Not ready: {e}')
    sys.exit(1)
" 2>/dev/null; do
    sleep 2
done

echo "Starting Apache..."
exec "$@"

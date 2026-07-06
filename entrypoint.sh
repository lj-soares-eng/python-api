#!/bin/sh
set -e

echo "Waiting for database..."
python - <<'PY'
import os
import time

import MySQLdb

host = os.environ.get("DB_HOST", "db")
port = int(os.environ.get("DB_PORT", "3306"))
user = os.environ.get("DB_USERNAME", "root")
password = os.environ.get("DB_PASSWORD", "")

for _ in range(30):
    try:
        MySQLdb.connect(host=host, port=port, user=user, passwd=password)
        break
    except Exception:
        time.sleep(2)
else:
    raise SystemExit("Database not ready")
PY

python manage.py migrate --noinput
exec "$@"

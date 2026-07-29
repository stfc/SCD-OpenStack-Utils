from flask import Blueprint, Response, current_app
from prometheus_client import (
    generate_latest, CONTENT_TYPE_LATEST,
    Gauge, Counter, REGISTRY,
)

metrics_bp = Blueprint('metrics', __name__)

# Custom application metrics
quota_requests_total = Gauge(
    'cloudtracker_quota_requests_total',
    'Total number of quota change requests',
)
quota_requests_by_status = Gauge(
    'cloudtracker_quota_requests_by_status',
    'Quota change requests broken down by status',
    ['status'],
)
snapshots_total = Gauge(
    'cloudtracker_snapshots_total',
    'Total number of database snapshots taken',
)
last_snapshot_timestamp = Gauge(
    'cloudtracker_last_snapshot_timestamp_seconds',
    'Unix timestamp of the most recent database snapshot',
)


@metrics_bp.route('/metrics')
def prometheus_metrics():
    """Prometheus scrape endpoint. Restrict to internal network via Apache config."""
    _refresh_metrics()
    return Response(generate_latest(REGISTRY), mimetype=CONTENT_TYPE_LATEST)


def _refresh_metrics():
    from .models import QuotaChange, DbSnapshot
    try:
        quota_requests_total.set(QuotaChange.query.count())
        for status in QuotaChange.STATUSES:
            quota_requests_by_status.labels(status=status).set(
                QuotaChange.query.filter_by(status=status).count()
            )
        snap_count = DbSnapshot.query.count()
        snapshots_total.set(snap_count)
        last_snap = DbSnapshot.query.order_by(DbSnapshot.snapshot_time.desc()).first()
        if last_snap and last_snap.snapshot_time:
            last_snapshot_timestamp.set(last_snap.snapshot_time.timestamp())
    except Exception:
        pass

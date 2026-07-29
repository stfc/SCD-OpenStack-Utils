from flask import Blueprint, Response
from prometheus_client import (
    generate_latest, CONTENT_TYPE_LATEST,
    Gauge, REGISTRY,
)

metrics_bp = Blueprint('metrics', __name__)

# Custom application metrics
tracked_projects_total = Gauge(
    'cloudtracker_tracked_projects_total',
    'Total number of projects with a recorded quota snapshot',
)
quota_snapshots_total = Gauge(
    'cloudtracker_quota_snapshots_total',
    'Total number of quota snapshots recorded',
)
funding_parties_total = Gauge(
    'cloudtracker_funding_parties_total',
    'Total number of funding parties defined',
)
project_quota = Gauge(
    'cloudtracker_project_quota',
    'Latest recorded quota value per project and field',
    ['project', 'field'],
)


@metrics_bp.route('/metrics')
def prometheus_metrics():
    """Prometheus scrape endpoint. Restrict to internal network via Apache config."""
    _refresh_metrics()
    return Response(generate_latest(REGISTRY), mimetype=CONTENT_TYPE_LATEST)


def _refresh_metrics():
    from . import db
    from .models import QuotaSnapshot, FundingParty, QUOTA_FIELD_KEYS
    try:
        quota_snapshots_total.set(QuotaSnapshot.query.count())
        funding_parties_total.set(FundingParty.query.count())

        project_names = [r[0] for r in db.session.query(QuotaSnapshot.project_name).distinct()]
        tracked_projects_total.set(len(project_names))
        for project_name in project_names:
            latest = (QuotaSnapshot.query
                      .filter_by(project_name=project_name)
                      .order_by(QuotaSnapshot.recorded_at.desc())
                      .first())
            for key in QUOTA_FIELD_KEYS:
                val = getattr(latest, key)
                if val is not None:
                    project_quota.labels(project=project_name, field=key).set(val)
    except Exception:
        pass

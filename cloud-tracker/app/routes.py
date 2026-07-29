from flask import Blueprint, render_template
from . import db
from .models import QuotaSnapshot, QuotaChangeLogEntry, FundingParty, QUOTA_FIELDS, QUOTA_FIELD_KEYS
from .auth import login_required

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@login_required
def index():
    total_projects = db.session.query(QuotaSnapshot.project_name).distinct().count()
    total_records = QuotaSnapshot.query.count()
    last_entry = db.session.query(db.func.max(QuotaSnapshot.recorded_at)).scalar()
    total_parties = FundingParty.query.count()

    # Latest snapshot per project (current allocations)
    latest_ids = (db.session.query(db.func.max(QuotaSnapshot.id))
                  .group_by(QuotaSnapshot.project_name).all())
    current_allocations = (QuotaSnapshot.query
                           .filter(QuotaSnapshot.id.in_([i for (i,) in latest_ids]))
                           .order_by(QuotaSnapshot.project_name).all())

    totals = {k: 0 for k in QUOTA_FIELD_KEYS}
    for snap in current_allocations:
        for k in QUOTA_FIELD_KEYS:
            val = getattr(snap, k)
            if val is not None:
                totals[k] += val

    # Recent change events (snapshots with at least one changed field)
    recent_events = []
    for snap in (QuotaSnapshot.query.order_by(QuotaSnapshot.recorded_at.desc()).limit(20).all()):
        changed_count = QuotaChangeLogEntry.query.filter_by(
            snapshot_id=snap.id, status='changed').count()
        if changed_count > 0:
            recent_events.append({'snapshot': snap, 'changed_count': changed_count})
        if len(recent_events) >= 8:
            break

    return render_template('index.html',
        total_projects=total_projects,
        total_records=total_records,
        total_parties=total_parties,
        last_entry=last_entry,
        current_allocations=current_allocations,
        recent_events=recent_events,
        quota_fields=QUOTA_FIELDS,
        totals=totals,
    )


# ── Error handlers ─────────────────────────────────────────────────────────────

@main_bp.app_errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403


@main_bp.app_errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

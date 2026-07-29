from datetime import datetime, timezone
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, jsonify, abort, current_app,
)
from . import db
from .models import QuotaChange, DbSnapshot
from .auth import login_required, admin_required, current_user, is_admin
from .snapshot import take_manual_snapshot

main_bp = Blueprint('main', __name__)


@main_bp.context_processor
def inject_globals():
    return {
        'site_title': current_app.config.get('SITE_TITLE', 'STFC Cloud Tracker'),
        'current_user': current_user(),
        'is_admin': is_admin(),
    }


@main_bp.route('/')
@login_required
def index():
    total = QuotaChange.query.count()
    pending = QuotaChange.query.filter_by(status='pending').count()
    approved = QuotaChange.query.filter_by(status='approved').count()
    rejected = QuotaChange.query.filter_by(status='rejected').count()
    in_progress = QuotaChange.query.filter_by(status='in_progress').count()
    last_snapshot = DbSnapshot.query.order_by(DbSnapshot.snapshot_time.desc()).first()
    recent = (QuotaChange.query
              .order_by(QuotaChange.created_at.desc())
              .limit(5).all())
    return render_template('index.html',
                           total=total,
                           pending=pending,
                           approved=approved,
                           rejected=rejected,
                           in_progress=in_progress,
                           last_snapshot=last_snapshot,
                           recent=recent)


# ── Quota changes ──────────────────────────────────────────────────────────────

@main_bp.route('/quota-changes', methods=['GET'])
@login_required
def quota_changes():
    status_filter = request.args.get('status', '')
    project_filter = request.args.get('project', '')

    q = QuotaChange.query
    if status_filter and status_filter in QuotaChange.STATUSES:
        q = q.filter_by(status=status_filter)
    if project_filter:
        q = q.filter(QuotaChange.project_name.ilike(f'%{project_filter}%'))

    changes = q.order_by(QuotaChange.created_at.desc()).all()
    return render_template(
        'quota_changes.html',
        changes=changes,
        quota_types=QuotaChange.QUOTA_TYPES,
        status_filter=status_filter,
        project_filter=project_filter,
        statuses=QuotaChange.STATUSES,
    )


@main_bp.route('/quota-changes/new', methods=['POST'])
@login_required
def quota_change_new():
    user = current_user()
    quota_type = request.form.get('quota_type', '').strip()
    unit = next((t[2] for t in QuotaChange.QUOTA_TYPES if t[0] == quota_type), '')

    try:
        current_val = int(request.form['current_value'])
        requested_val = int(request.form['requested_value'])
    except (ValueError, KeyError):
        flash('Current and requested values must be integers.', 'error')
        return redirect(url_for('main.quota_changes'))

    change = QuotaChange(
        project_name=request.form.get('project_name', '').strip(),
        quota_type=quota_type,
        current_value=current_val,
        requested_value=requested_val,
        unit=unit,
        justification=request.form.get('justification', '').strip(),
        requester_name=user['name'],
        requester_email=user['email'],
        status='pending',
    )
    db.session.add(change)
    db.session.commit()
    flash('Quota change request submitted successfully.', 'success')
    return redirect(url_for('main.quota_changes'))


@main_bp.route('/quota-changes/<int:change_id>/update', methods=['POST'])
@admin_required
def quota_change_update(change_id):
    change = QuotaChange.query.get_or_404(change_id)
    new_status = request.form.get('status', '').strip()
    if new_status not in QuotaChange.STATUSES:
        flash('Invalid status.', 'error')
        return redirect(url_for('main.quota_changes'))

    change.status = new_status
    change.admin_notes = request.form.get('admin_notes', '').strip() or change.admin_notes
    change.processed_by = current_user()['email']
    change.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    flash(f'Request #{change_id} updated to {new_status}.', 'success')
    return redirect(url_for('main.quota_changes'))


# ── Snapshots ──────────────────────────────────────────────────────────────────

@main_bp.route('/snapshots')
@login_required
def snapshots():
    snaps = DbSnapshot.query.order_by(DbSnapshot.snapshot_time.desc()).limit(50).all()
    return render_template('snapshots.html', snapshots=snaps)


@main_bp.route('/snapshots/create', methods=['POST'])
@admin_required
def snapshot_create():
    user = current_user()
    take_manual_snapshot(created_by=user['email'])
    flash('Snapshot created successfully.', 'success')
    return redirect(url_for('main.snapshots'))


@main_bp.route('/snapshots/<int:snap_id>')
@login_required
def snapshot_detail(snap_id):
    snap = DbSnapshot.query.get_or_404(snap_id)
    return jsonify(snap.snapshot_data)


# ── Error handlers ─────────────────────────────────────────────────────────────

@main_bp.app_errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403


@main_bp.app_errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

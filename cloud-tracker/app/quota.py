from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, jsonify,
)
from . import db
from .auth import login_required, current_user
from .models import (
    QuotaSnapshot, QuotaChangeLogEntry, FundingParty, PartyProject,
    QUOTA_FIELDS, QUOTA_FIELD_KEYS, QUOTA_FIELD_LABELS,
)

quota_bp = Blueprint('quota', __name__, url_prefix='/quota')


def _known_projects():
    rows = (db.session.query(QuotaSnapshot.project_name)
            .distinct().order_by(QuotaSnapshot.project_name).all())
    return [r[0] for r in rows]


def _latest_snapshot(project_name):
    return (QuotaSnapshot.query
            .filter_by(project_name=project_name)
            .order_by(QuotaSnapshot.recorded_at.desc())
            .first())


# ── Quota entry ───────────────────────────────────────────────────────────────

@quota_bp.route('/entry', methods=['GET'])
@login_required
def entry():
    return render_template('quota_entry.html',
        quota_fields=QUOTA_FIELDS,
        projects=_known_projects(),
        form_data=None,
    )


@quota_bp.route('/entry', methods=['POST'])
@login_required
def entry_post():
    project_name = request.form.get('project_name', '').strip()

    def _rerender(error_msg):
        flash(error_msg, 'error')
        return render_template('quota_entry.html',
            quota_fields=QUOTA_FIELDS,
            projects=_known_projects(),
            form_data=request.form,
        )

    if not project_name:
        return _rerender('Project name is required.')

    entered = {}
    for key, label, _unit in QUOTA_FIELDS:
        raw = request.form.get(key, '').strip()
        if raw == '':
            entered[key] = None
        else:
            try:
                entered[key] = int(float(raw))
            except ValueError:
                return _rerender(f'Invalid value for {label}: "{raw}" — please enter a whole number.')

    if all(v is None for v in entered.values()):
        return _rerender('At least one quota field must be filled in.')

    result = _record_quota(project_name, entered, current_user()['email'])
    if result['is_first']:
        flash(f'Baseline recorded for "{project_name}".', 'success')
    elif result['changed_count'] > 0:
        flash(f'{result["changed_count"]} field(s) changed for "{project_name}".', 'success')
    else:
        flash(f'No changes detected for "{project_name}" — values recorded.', 'info')

    return redirect(url_for('quota.log'))


def _record_quota(project_name, entered, recorded_by):
    """entered: dict {field_key: int or None}. None = carry previous value forward."""
    prev = _latest_snapshot(project_name)
    is_first = prev is None

    snap_values = {}
    for key in QUOTA_FIELD_KEYS:
        if entered[key] is not None:
            snap_values[key] = entered[key]
        elif prev is not None:
            snap_values[key] = getattr(prev, key)
        else:
            snap_values[key] = None

    snapshot = QuotaSnapshot(project_name=project_name, recorded_by=recorded_by, **snap_values)
    db.session.add(snapshot)
    db.session.flush()  # assign snapshot.id

    changed_count = 0
    for key in QUOTA_FIELD_KEYS:
        new_val = snap_values[key]
        prev_val = getattr(prev, key) if prev else None

        if is_first:
            status, diff = 'new', None
        elif entered[key] is None:
            status, diff = 'unchanged', 0
        elif prev_val != new_val:
            status = 'changed'
            changed_count += 1
            diff = (new_val - prev_val) if (new_val is not None and prev_val is not None) else None
        else:
            status, diff = 'unchanged', 0

        db.session.add(QuotaChangeLogEntry(
            snapshot_id=snapshot.id, project_name=project_name, field_name=key,
            previous_value=prev_val, new_value=new_val, difference=diff, status=status,
        ))

    db.session.commit()
    return {'snapshot_id': snapshot.id, 'is_first': is_first, 'changed_count': changed_count}


# ── Change log ────────────────────────────────────────────────────────────────

@quota_bp.route('/log')
@login_required
def log():
    project_filter = request.args.get('project', '')
    changed_only = request.args.get('changed_only', '1') == '1'

    query = (db.session.query(QuotaSnapshot)
             .order_by(QuotaSnapshot.recorded_at.desc()))
    if project_filter:
        query = query.filter(QuotaSnapshot.project_name == project_filter)
    snapshots = query.limit(100).all()

    events = []
    for snap in snapshots:
        changes = (QuotaChangeLogEntry.query
                   .filter_by(snapshot_id=snap.id)
                   .order_by(QuotaChangeLogEntry.field_name).all())
        changed_count = sum(1 for c in changes if c.status == 'changed')
        new_count = sum(1 for c in changes if c.status == 'new')
        if changed_only and changed_count == 0 and new_count == 0:
            continue
        events.append({
            'id': snap.id, 'project_name': snap.project_name,
            'recorded_at': snap.recorded_at, 'recorded_by': snap.recorded_by,
            'changed_count': changed_count, 'new_count': new_count,
            'changes': changes,
        })

    return render_template('quota_log.html',
        events=events,
        projects=_known_projects(),
        project_filter=project_filter,
        changed_only=changed_only,
        field_labels=QUOTA_FIELD_LABELS,
    )


# ── Raw snapshot listing ─────────────────────────────────────────────────────

@quota_bp.route('/snapshots')
@login_required
def snapshots():
    project_filter = request.args.get('project', '')
    query = QuotaSnapshot.query.order_by(QuotaSnapshot.recorded_at.desc())
    if project_filter:
        query = query.filter_by(project_name=project_filter)
    rows = query.limit(200).all()
    return render_template('quota_snapshots.html',
        snapshots=rows,
        projects=_known_projects(),
        project_filter=project_filter,
        quota_fields=QUOTA_FIELDS,
    )


# ── Funding parties ───────────────────────────────────────────────────────────

@quota_bp.route('/parties')
@login_required
def parties():
    parties = FundingParty.query.order_by(FundingParty.name).all()

    result = []
    for party in parties:
        proj_names = [pp.project_name for pp in
                      PartyProject.query.filter_by(party_id=party.id)
                      .order_by(PartyProject.project_name).all()]

        party_projects = []
        party_totals = {k: 0 for k in QUOTA_FIELD_KEYS}
        for pname in proj_names:
            snap = _latest_snapshot(pname)
            if snap:
                party_projects.append(snap)
                for k in QUOTA_FIELD_KEYS:
                    val = getattr(snap, k)
                    if val is not None:
                        party_totals[k] += val
            else:
                party_projects.append({'project_name': pname, 'recorded_at': None, 'recorded_by': None})

        result.append({
            'id': party.id, 'name': party.name,
            'projects': party_projects, 'totals': party_totals,
            'project_count': len(proj_names),
        })

    return render_template('quota_parties.html',
        parties=result,
        all_projects=_known_projects(),
        quota_fields=QUOTA_FIELDS,
    )


@quota_bp.route('/parties/new', methods=['POST'])
@login_required
def parties_new():
    name = request.form.get('name', '').strip()
    if not name:
        flash('Party name is required.', 'error')
        return redirect(url_for('quota.parties'))
    db.session.add(FundingParty(name=name))
    db.session.commit()
    flash(f'Funding party "{name}" created.', 'success')
    return redirect(url_for('quota.parties'))


@quota_bp.route('/parties/<int:party_id>/add-project', methods=['POST'])
@login_required
def parties_add_project(party_id):
    project_name = request.form.get('project_name', '').strip()
    if not project_name:
        flash('Project name is required.', 'error')
        return redirect(url_for('quota.parties'))
    db.session.add(PartyProject(party_id=party_id, project_name=project_name))
    db.session.commit()
    flash(f'Project "{project_name}" added.', 'success')
    return redirect(url_for('quota.parties'))


@quota_bp.route('/parties/<int:party_id>/remove-project', methods=['POST'])
@login_required
def parties_remove_project(party_id):
    project_name = request.form.get('project_name', '').strip()
    PartyProject.query.filter_by(party_id=party_id, project_name=project_name).delete()
    db.session.commit()
    flash(f'Project "{project_name}" removed.', 'success')
    return redirect(url_for('quota.parties'))


@quota_bp.route('/parties/<int:party_id>/delete', methods=['POST'])
@login_required
def parties_delete(party_id):
    party = db.session.get(FundingParty, party_id)
    if party:
        name = party.name
        db.session.delete(party)
        db.session.commit()
        flash(f'Funding party "{name}" deleted.', 'success')
    return redirect(url_for('quota.parties'))


# ── API endpoints ─────────────────────────────────────────────────────────────

@quota_bp.route('/api/projects')
@login_required
def api_projects():
    return jsonify({'projects': _known_projects()})


@quota_bp.route('/api/project/<project_name>/current')
@login_required
def api_project_current(project_name):
    snap = _latest_snapshot(project_name)
    if not snap:
        return jsonify({'found': False})
    values = {k: getattr(snap, k) for k in QUOTA_FIELD_KEYS}
    return jsonify({'found': True, 'values': values})

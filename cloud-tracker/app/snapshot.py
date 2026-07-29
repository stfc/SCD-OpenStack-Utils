from datetime import datetime, timezone


def take_scheduled_snapshot(app):
    with app.app_context():
        _do_snapshot(snapshot_type='scheduled', created_by='system')


def take_manual_snapshot(created_by: str):
    from . import db
    _do_snapshot(snapshot_type='manual', created_by=created_by)


def _do_snapshot(snapshot_type: str, created_by: str):
    from . import db
    from .models import QuotaChange, DbSnapshot

    rows = QuotaChange.query.all()
    data = [r.to_dict() for r in rows]

    snap = DbSnapshot(
        snapshot_time=datetime.now(timezone.utc),
        snapshot_type=snapshot_type,
        record_count=len(data),
        snapshot_data={'quota_changes': data},
        created_by=created_by,
    )
    db.session.add(snap)
    db.session.commit()
    return snap

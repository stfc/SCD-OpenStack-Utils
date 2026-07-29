from datetime import datetime, timezone
from . import db


class QuotaChange(db.Model):
    __tablename__ = 'quota_changes'

    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(255), nullable=False, index=True)
    quota_type = db.Column(db.String(100), nullable=False)
    current_value = db.Column(db.Integer, nullable=False)
    requested_value = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(50), nullable=False, default='')
    justification = db.Column(db.Text, nullable=False)
    requester_name = db.Column(db.String(255), nullable=False)
    requester_email = db.Column(db.String(255), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default='pending', index=True)
    admin_notes = db.Column(db.Text, nullable=True)
    processed_by = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    STATUSES = ('pending', 'approved', 'rejected', 'in_progress')

    QUOTA_TYPES = [
        ('instances',    'Instances',       'count'),
        ('cores',        'CPU Cores',       'cores'),
        ('ram',          'RAM',             'GB'),
        ('volumes',      'Volumes',         'count'),
        ('gigabytes',    'Storage',         'GB'),
        ('snapshots',    'Snapshots',       'count'),
        ('floating_ips', 'Floating IPs',    'count'),
        ('security_groups', 'Security Groups', 'count'),
        ('networks',     'Networks',        'count'),
        ('routers',      'Routers',         'count'),
        ('ports',        'Ports',           'count'),
        ('object_storage', 'Object Storage', 'GB'),
    ]

    def to_dict(self):
        return {
            'id': self.id,
            'project_name': self.project_name,
            'quota_type': self.quota_type,
            'current_value': self.current_value,
            'requested_value': self.requested_value,
            'unit': self.unit,
            'justification': self.justification,
            'requester_name': self.requester_name,
            'requester_email': self.requester_email,
            'status': self.status,
            'admin_notes': self.admin_notes,
            'processed_by': self.processed_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class DbSnapshot(db.Model):
    __tablename__ = 'db_snapshots'

    id = db.Column(db.Integer, primary_key=True)
    snapshot_time = db.Column(db.DateTime, nullable=False,
                              default=lambda: datetime.now(timezone.utc), index=True)
    snapshot_type = db.Column(db.String(20), nullable=False, default='scheduled')
    record_count = db.Column(db.Integer, nullable=False, default=0)
    snapshot_data = db.Column(db.JSON, nullable=False, default=dict)
    created_by = db.Column(db.String(255), nullable=True)

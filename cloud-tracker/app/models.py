from datetime import datetime, timezone
from . import db


# ── Quota allocation tracking (funding parties, manual entry, change log) ────

QUOTA_FIELDS = [
    ('cpu_cores',            'CPU Cores',            'cores'),
    ('instances',            'Instances',            ''),
    ('ram_gb',               'RAM',                  'GB'),
    ('floating_ips',         'Floating IPs',         ''),
    ('security_group_rules', 'Security Group Rules', ''),
    ('cinder_storage_gb',    'Cinder Storage',       'GB'),
    ('backups',              'Backups',              ''),
    ('security_groups',      'Security Groups',      ''),
    ('snapshots_count',      'Snapshots',            ''),
    ('volumes',              'Volumes',              ''),
]
QUOTA_FIELD_KEYS = [f[0] for f in QUOTA_FIELDS]
QUOTA_FIELD_LABELS = {f[0]: f[1] for f in QUOTA_FIELDS}
QUOTA_FIELD_UNITS = {f[0]: f[2] for f in QUOTA_FIELDS}


class QuotaSnapshot(db.Model):
    __tablename__ = 'quota_snapshots'

    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(255), nullable=False, index=True)
    recorded_by = db.Column(db.String(255), nullable=True)
    recorded_at = db.Column(db.DateTime, nullable=False,
                            default=lambda: datetime.now(timezone.utc), index=True)
    cpu_cores = db.Column(db.Integer, nullable=True)
    instances = db.Column(db.Integer, nullable=True)
    ram_gb = db.Column(db.Integer, nullable=True)
    floating_ips = db.Column(db.Integer, nullable=True)
    security_group_rules = db.Column(db.Integer, nullable=True)
    cinder_storage_gb = db.Column(db.Integer, nullable=True)
    backups = db.Column(db.Integer, nullable=True)
    security_groups = db.Column(db.Integer, nullable=True)
    snapshots_count = db.Column(db.Integer, nullable=True)
    volumes = db.Column(db.Integer, nullable=True)


class QuotaChangeLogEntry(db.Model):
    __tablename__ = 'quota_change_log'

    id = db.Column(db.Integer, primary_key=True)
    snapshot_id = db.Column(db.Integer, db.ForeignKey('quota_snapshots.id', ondelete='CASCADE'),
                            nullable=False, index=True)
    project_name = db.Column(db.String(255), nullable=False, index=True)
    field_name = db.Column(db.String(100), nullable=False, index=True)
    previous_value = db.Column(db.Integer, nullable=True)
    new_value = db.Column(db.Integer, nullable=True)
    difference = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='unchanged', index=True)
    recorded_at = db.Column(db.DateTime, nullable=False,
                            default=lambda: datetime.now(timezone.utc), index=True)


class FundingParty(db.Model):
    __tablename__ = 'funding_parties'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


class PartyProject(db.Model):
    __tablename__ = 'party_projects'

    id = db.Column(db.Integer, primary_key=True)
    party_id = db.Column(db.Integer, db.ForeignKey('funding_parties.id', ondelete='CASCADE'),
                         nullable=False, index=True)
    project_name = db.Column(db.String(255), nullable=False, index=True)

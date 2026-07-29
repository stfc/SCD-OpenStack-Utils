import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from apscheduler.schedulers.background import BackgroundScheduler

db = SQLAlchemy()
oauth = OAuth()
scheduler = BackgroundScheduler(daemon=True)


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SITE_TITLE'] = os.environ.get('SITE_TITLE', 'STFC Cloud Tracker')
    app.config['APP_BASE_URL'] = os.environ.get('APP_BASE_URL', '')
    admin_raw = os.environ.get('ADMIN_EMAILS', '')
    app.config['ADMIN_EMAILS'] = [e.strip() for e in admin_raw.split(',') if e.strip()]

    db.init_app(app)
    oauth.init_app(app)

    oauth.register(
        name='iris_iam',
        client_id=os.environ['OIDC_CLIENT_ID'],
        client_secret=os.environ['OIDC_CLIENT_SECRET'],
        server_metadata_url=os.environ['OIDC_DISCOVERY_URL'],
        client_kwargs={
            'scope': 'openid email profile',
        },
    )

    from .auth import auth_bp
    from .routes import main_bp
    from .metrics import metrics_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(metrics_bp)

    with app.app_context():
        db.create_all()
        _start_scheduler(app)

    return app


def _start_scheduler(app):
    from .snapshot import take_scheduled_snapshot

    if not scheduler.running:
        scheduler.add_job(
            func=take_scheduled_snapshot,
            args=[app],
            trigger='interval',
            hours=6,
            id='db_snapshot',
            replace_existing=True,
        )
        scheduler.start()

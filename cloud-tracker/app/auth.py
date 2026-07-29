from flask import (
    Blueprint, redirect, url_for, session,
    request, current_app, render_template, flash,
)
from functools import wraps
from . import oauth

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            session['next'] = request.url
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            session['next'] = request.url
            return redirect(url_for('auth.login'))
        user_email = session['user'].get('email', '')
        if user_email not in current_app.config.get('ADMIN_EMAILS', []):
            return render_template('403.html'), 403
        return f(*args, **kwargs)
    return decorated


def current_user():
    return session.get('user')


def is_admin():
    user = current_user()
    if not user:
        return False
    return user.get('email', '') in current_app.config.get('ADMIN_EMAILS', [])


@auth_bp.route('/login')
def login():
    redirect_uri = current_app.config['APP_BASE_URL'] + url_for('auth.callback')
    return oauth.iris_iam.authorize_redirect(redirect_uri)


@auth_bp.route('/callback')
def callback():
    token = oauth.iris_iam.authorize_access_token()
    userinfo = token.get('userinfo') or oauth.iris_iam.userinfo()
    session['user'] = {
        'sub':   userinfo.get('sub'),
        'name':  userinfo.get('name', userinfo.get('preferred_username', 'Unknown')),
        'email': userinfo.get('email', ''),
    }
    next_url = session.pop('next', None)
    return redirect(next_url or url_for('main.index'))


@auth_bp.route('/logout')
def logout():
    session.clear()
    # Redirect to OIDC end_session_endpoint if available
    try:
        meta = oauth.iris_iam.load_server_metadata()
        end_session = meta.get('end_session_endpoint')
        if end_session:
            post_logout = current_app.config['APP_BASE_URL'] + url_for('main.index')
            return redirect(f"{end_session}?post_logout_redirect_uri={post_logout}")
    except Exception:
        pass
    return redirect(url_for('main.index'))

from datetime import timezone
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None

PERU_TZ = 'America/Lima'
TIMEZONE_LABELS = {
    'America/Lima': 'Perú',
    'America/Bogota': 'Colombia',
    'America/Santiago': 'Chile',
    'America/Argentina/Buenos_Aires': 'Argentina',
    'America/Montevideo': 'Uruguay',
    'America/La_Paz': 'Bolivia',
    'America/Caracas': 'Venezuela',
    'America/Guayaquil': 'Ecuador',
    'America/Sao_Paulo': 'Brasil',
    'America/Mexico_City': 'México',
    'America/New_York': 'EE.UU.',
    'America/Chicago': 'EE.UU.',
    'America/Denver': 'EE.UU.',
    'America/Los_Angeles': 'EE.UU.',
}


def timezone_label(tz_name):
    if not tz_name:
        return 'Local'
    if tz_name in TIMEZONE_LABELS:
        return TIMEZONE_LABELS[tz_name]
    label = tz_name.split('/')[-1].replace('_', ' ')
    if label.startswith('GMT'):
        return label
    return label


def format_datetime(value, fmt='%d/%m/%Y %H:%M', tz=PERU_TZ):
    if not value:
        return ''
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    if ZoneInfo is None or tz == 'UTC':
        return value.strftime(fmt)
    try:
        return value.astimezone(ZoneInfo(tz)).strftime(fmt)
    except Exception:
        return value.strftime(fmt)


def format_datetime_dual(value, local_tz=None, fmt='%H:%M'):
    if not value:
        return ''

    peru_time = format_datetime(value, fmt, PERU_TZ)
    if not local_tz or local_tz == PERU_TZ:
        return f'{peru_time} (Perú)'

    local_label = timezone_label(local_tz)
    try:
        local_time = format_datetime(value, fmt, local_tz)
        return f'{peru_time} (Perú) - {local_time} ({local_label})'
    except Exception:
        return f'{peru_time} (Perú) - {local_label}'


def ensure_timezone_column(app):
    with app.app_context():
        db.create_all()
        inspector = inspect(db.engine)
        if 'respuestas_encuesta' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('respuestas_encuesta')]
            if 'timezone' not in columns:
                dialect = db.engine.dialect.name
                alter_sql = 'ALTER TABLE respuestas_encuesta ADD COLUMN timezone VARCHAR(64) NULL'
                if dialect == 'sqlite':
                    alter_sql = 'ALTER TABLE respuestas_encuesta ADD COLUMN timezone VARCHAR(64)'
                db.session.execute(text(alter_sql))
                db.session.commit()


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app.routes.admin import admin_bp
    from app.routes.user import user_bp

    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/')

    ensure_timezone_column(app)

    app.jinja_env.filters['format_datetime'] = format_datetime
    app.jinja_env.filters['format_datetime_dual'] = format_datetime_dual
    app.jinja_env.filters['timezone_label'] = timezone_label

    return app
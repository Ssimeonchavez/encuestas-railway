from collections import Counter
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models import Encuesta, Pregunta, RespuestaEncuesta, Usuario
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

admin_bp = Blueprint('admin', __name__, template_folder='../templates/admin')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('admin.login'))
        user = Usuario.query.get(session['user_id'])
        if not user or not user.es_admin:
            flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
            return redirect(url_for('user.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['es_admin'] = user.es_admin
            flash(f'Bienvenido, {user.username}!', 'success')
            if user.es_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('user.index'))
        
        flash('Usuario o contraseña incorrectos.', 'danger')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('admin.login'))

@admin_bp.route('/')
@admin_required
def dashboard():
    encuestas = Encuesta.query.order_by(Encuesta.fecha_creacion.desc()).all()
    return render_template('admin/dashboard.html', encuestas=encuestas)

@admin_bp.route('/encuesta/crear', methods=['GET', 'POST'])
@admin_required
def crear_encuesta():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        recolectar_ubicacion = request.form.get('recolectar_ubicacion') == 'on'

        encuesta = Encuesta(
            titulo=titulo,
            descripcion=descripcion,
            recolectar_ubicacion=recolectar_ubicacion,
            creador_id=session['user_id']
        )
        db.session.add(encuesta)
        db.session.flush()  # Para obtener el ID
        
        # Procesar preguntas
        preguntas_texto = request.form.getlist('pregunta_texto[]')
        preguntas_tipo = request.form.getlist('pregunta_tipo[]')
        preguntas_opciones = request.form.getlist('pregunta_opciones[]')
        
        for i, (texto, tipo, opciones) in enumerate(zip(preguntas_texto, preguntas_tipo, preguntas_opciones)):
            if texto.strip():
                pregunta = Pregunta(
                    encuesta_id=encuesta.id,
                    texto=texto,
                    tipo=tipo,
                    opciones=opciones if tipo == 'opcion_multiple' else None,
                    orden=i
                )
                db.session.add(pregunta)
        
        db.session.commit()
        flash('Encuesta creada exitosamente.', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/crear_encuesta.html')

@admin_bp.route('/encuesta/<int:id>/resultados')
@admin_required
def ver_resultados(id):
    encuesta = Encuesta.query.get_or_404(id)
    ubicaciones_count = sum(1 for r in encuesta.respuestas if r.latitude is not None and r.longitude is not None)
    fuera_peru_count = sum(1 for r in encuesta.respuestas if (r.timezone or 'America/Lima') != 'America/Lima')
    return render_template('admin/ver_resultados.html', encuesta=encuesta, ubicaciones_count=ubicaciones_count, fuera_peru_count=fuera_peru_count)

@admin_bp.route('/estadisticas')
@admin_required
def estadisticas():
    def parse_date(value):
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except (TypeError, ValueError):
            return None

    start_date = parse_date(request.args.get('start_date'))
    end_date = parse_date(request.args.get('end_date'))
    if start_date and end_date and start_date > end_date:
        start_date, end_date = end_date, start_date

    def in_range(fecha):
        if not start_date and not end_date:
            return True
        fecha_date = fecha.date()
        if start_date and fecha_date < start_date:
            return False
        if end_date and fecha_date > end_date:
            return False
        return True

    encuestas = Encuesta.query.order_by(Encuesta.fecha_creacion.desc()).all()
    total_encuestas = len(encuestas)
    total_preguntas = sum(len(e.preguntas) for e in encuestas)
    total_respuestas = sum(1 for e in encuestas for r in e.respuestas if in_range(r.fecha_completada))
    total_ubicaciones = sum(
        1
        for e in encuestas
        for r in e.respuestas
        if r.latitude is not None and r.longitude is not None and in_range(r.fecha_completada)
    )
    active_encuestas = sum(1 for e in encuestas if e.activa)
    respuestas_por_encuesta = [
        {
            'id': e.id,
            'titulo': e.titulo,
            'respuestas': sum(1 for r in e.respuestas if in_range(r.fecha_completada)),
            'preguntas': len(e.preguntas),
            'ubicaciones': sum(1 for r in e.respuestas if r.latitude is not None and r.longitude is not None and in_range(r.fecha_completada)),
            'activa': e.activa,
        }
        for e in encuestas
    ]
    selected_id = request.args.get('id', type=int)
    selected_encuesta = None
    if selected_id:
        selected_encuesta = Encuesta.query.get(selected_id)
    if not selected_encuesta and encuestas:
        selected_encuesta = encuestas[0]
        selected_id = selected_encuesta.id

    selected_stats = None
    timeline_labels = []
    timeline_values = []
    if selected_encuesta:
        filtered_respuestas = [r for r in selected_encuesta.respuestas if in_range(r.fecha_completada)]
        selected_stats = {
            'id': selected_encuesta.id,
            'titulo': selected_encuesta.titulo,
            'respuestas': len(filtered_respuestas),
            'preguntas': len(selected_encuesta.preguntas),
            'ubicaciones': sum(1 for r in filtered_respuestas if r.latitude is not None and r.longitude is not None),
            'activa': selected_encuesta.activa,
        }
        dates = [r.fecha_completada.strftime('%d/%m/%Y') for r in filtered_respuestas]
        counter = Counter(dates)
        timeline_labels = sorted(counter.keys(), key=lambda d: tuple(map(int, d.split('/')[::-1])))
        timeline_values = [counter[label] for label in timeline_labels]

    return render_template(
        'admin/estadisticas.html',
        total_encuestas=total_encuestas,
        total_preguntas=total_preguntas,
        total_respuestas=total_respuestas,
        total_ubicaciones=total_ubicaciones,
        active_encuestas=active_encuestas,
        respuestas_por_encuesta=respuestas_por_encuesta,
        selected_stats=selected_stats,
        selected_id=selected_id,
        timeline_labels=timeline_labels,
        timeline_values=timeline_values,
        encuestas=encuestas,
        start_date=start_date,
        end_date=end_date,
    )

@admin_bp.route('/encuesta/<int:id>/toggle', methods=['POST'])
@admin_required
def toggle_encuesta(id):
    encuesta = Encuesta.query.get_or_404(id)
    encuesta.activa = not encuesta.activa
    db.session.commit()
    estado = 'activada' if encuesta.activa else 'desactivada'
    flash(f'Encuesta {estado}.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/encuesta/<int:id>/eliminar', methods=['POST'])
@admin_required
def eliminar_encuesta(id):
    encuesta = Encuesta.query.get_or_404(id)
    for respuesta_encuesta in encuesta.respuestas:
        db.session.delete(respuesta_encuesta)
    db.session.delete(encuesta)
    db.session.commit()
    flash('Encuesta eliminada.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/setup')
def setup():
    """Crea un usuario admin inicial. Eliminar o proteger en producción."""
    if Usuario.query.filter_by(username='admin').first():
        return 'Admin ya existe. <a href="/admin/login">Ir al login</a>'
    
    admin = Usuario(
        username='admin',
        email='admin@encuestas.com',
        password_hash=generate_password_hash('admin123'),
        es_admin=True
    )
    db.session.add(admin)
    db.session.commit()
    return 'Usuario admin creado. Username: admin | Password: admin123<br><a href="/admin/login">Ir al login</a>'
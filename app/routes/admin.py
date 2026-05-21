from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models import Encuesta, Pregunta, Usuario
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
    return render_template('admin/ver_resultados.html', encuesta=encuesta)

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
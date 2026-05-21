from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models import Encuesta, Pregunta, Respuesta, RespuestaEncuesta, Usuario
from functools import wraps

user_bp = Blueprint('user', __name__, template_folder='../templates/user')

@user_bp.route('/')
def index():
    encuestas = Encuesta.query.filter_by(activa=True).order_by(Encuesta.fecha_creacion.desc()).all()
    return render_template('user/encuestas.html', encuestas=encuestas)

@user_bp.route('/encuesta/<int:id>', methods=['GET', 'POST'])
def responder(id):
    encuesta = Encuesta.query.get_or_404(id)
    
    if not encuesta.activa:
        flash('Esta encuesta ya no está disponible.', 'warning')
        return redirect(url_for('user.index'))
    
    if request.method == 'POST':
        # Guardar respuestas
        respuesta_encuesta = RespuestaEncuesta(
            encuesta_id=id,
            ip_address=request.remote_addr
        )
        db.session.add(respuesta_encuesta)
        db.session.flush()
        
        for pregunta in encuesta.preguntas:
            valor = request.form.get(f'pregunta_{pregunta.id}', '')
            respuesta = Respuesta(
                pregunta_id=pregunta.id,
                respuesta_encuesta_id=respuesta_encuesta.id,
                valor=valor
            )
            db.session.add(respuesta)
        
        db.session.commit()
        flash('¡Gracias por completar la encuesta!', 'success')
        return redirect(url_for('user.index'))
    
    return render_template('user/responder.html', encuesta=encuesta)
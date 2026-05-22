from app import db
from datetime import datetime

class Encuesta(db.Model):
    __tablename__ = 'encuestas'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    recolectar_ubicacion = db.Column(db.Boolean, default=False)
    activa = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    creador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    
    preguntas = db.relationship('Pregunta', backref='encuesta', lazy=True, cascade='all, delete-orphan')
    respuestas = db.relationship('RespuestaEncuesta', backref='encuesta', lazy=True, cascade='all, delete-orphan')

class Pregunta(db.Model):
    __tablename__ = 'preguntas'
    
    id = db.Column(db.Integer, primary_key=True)
    encuesta_id = db.Column(db.Integer, db.ForeignKey('encuestas.id'), nullable=False)
    texto = db.Column(db.String(500), nullable=False)
    tipo = db.Column(db.String(20), default='texto')  # texto, opcion_multiple, escala
    opciones = db.Column(db.Text)  # JSON separado por comas para opciones múltiples
    orden = db.Column(db.Integer, default=0)
    
    respuestas = db.relationship('Respuesta', backref='pregunta', lazy=True)

class Respuesta(db.Model):
    __tablename__ = 'respuestas'
    
    id = db.Column(db.Integer, primary_key=True)
    pregunta_id = db.Column(db.Integer, db.ForeignKey('preguntas.id'), nullable=False)
    respuesta_encuesta_id = db.Column(db.Integer, db.ForeignKey('respuestas_encuesta.id'), nullable=False)
    valor = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

class RespuestaEncuesta(db.Model):
    __tablename__ = 'respuestas_encuesta'
    
    id = db.Column(db.Integer, primary_key=True)
    encuesta_id = db.Column(db.Integer, db.ForeignKey('encuestas.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    fecha_completada = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    respuestas = db.relationship('Respuesta', backref='respuesta_encuesta', lazy=True, cascade='all, delete-orphan')

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    es_admin = db.Column(db.Boolean, default=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    encuestas_creadas = db.relationship('Encuesta', backref='creador', lazy=True)
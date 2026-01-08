from flask_sqlalchemy import SQLAlchemy
from datetime import datetime as dt

# Inicializamos la extensión de base de datos
db = SQLAlchemy()

# --- TABLA 1: USUARIOS ---
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=dt.utcnow)
    
    # Relaciones:
    # Un usuario tiene UN perfil de dosha (uselist=False)
    dosha_profile = db.relationship('DoshaProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    # Un usuario tiene MUCHOS registros diarios (lazy=True para cargar solo cuando se pida)
    daily_logs = db.relationship('DailyLog', backref='user', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.email}>'

# --- TABLA 2: PERFIL AYURVÉDICO (Resultado del Test) ---
class DoshaProfile(db.Model):
    __tablename__ = 'dosha_profiles'
    id = db.Column(db.Integer, primary_key=True)
    # Clave foránea: Vincula este perfil a un usuario específico
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # El resultado principal, ej: "Vata", "Pitta-Kapha"
    dominant_dosha = db.Column(db.String(50), nullable=False)
    
    # Guardamos los puntajes crudos por si queremos mostrar porcentajes después
    vata_score = db.Column(db.Integer, default=0)
    pitta_score = db.Column(db.Integer, default=0)
    kapha_score = db.Column(db.Integer, default=0)
    
    updated_at = db.Column(db.DateTime, default=dt.utcnow, onupdate=dt.utcnow)

# --- TABLA 3: SEGUIMIENTO DIARIO (Plan de 90 Días) ---
class DailyLog(db.Model):
    __tablename__ = 'daily_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Fecha del registro. Importante: Solo un registro por usuario por día.
    date = db.Column(db.Date, nullable=False, default=dt.utcnow().date)
    
    # Los "No Negociables" del mantenimiento ayurvédico (Booleanos: Sí/No)
    # 1. Horario de Sueño Consistente
    slept_consistently = db.Column(db.Boolean, default=False)
    # 2. Principios Alimentarios Básicos (Dieta 80/20)
    followed_diet = db.Column(db.Boolean, default=False)
    # 3. Práctica Mente-Cuerpo Diaria (Meditación/Pranayama 10 min)
    mind_body_practice = db.Column(db.Boolean, default=False)
    # 4. Movimiento Regular (Ejercicio apropiado)
    movement = db.Column(db.Boolean, default=False)
    
    # Espacio para journaling emocional o síntomas (Diario de síntomas)
    notes = db.Column(db.Text, nullable=True)

    # Restricción única: Un usuario no puede tener dos logs el mismo día
    __table_args__ = (db.UniqueConstraint('user_id', 'date', name='_user_date_uc'),)
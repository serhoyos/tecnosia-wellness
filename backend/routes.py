from datetime import datetime as dt
from backend.models import DailyLog
from flask import Blueprint, request, jsonify
from backend.models import db, User, DoshaProfile

# Creamos un "Blueprint" para agrupar estas rutas.
# Esto ayuda a organizar el código en aplicaciones grandes.
api = Blueprint('api', __name__)

# --- RUTA 1: REGISTRO DE USUARIOS ---
@api.route('/register', methods=['POST'])
def register():
    # 1. Obtener los datos enviados por el frontend (en formato JSON)
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # 2. Validaciones básicas
    if not email or not password:
        return jsonify({'message': 'Faltan datos'}), 400
    
    # 3. Verificar si el usuario ya existe
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'message': 'El usuario ya existe'}), 400

    # 4. Crear el nuevo usuario
    # IMPORTANTE: En una app real, AQUÍ se debe hashear la contraseña antes de guardarla.
    # Por ahora, para facilitar las pruebas iniciales, la guardaremos en texto plano.
    # Lo actualizaremos a bcrypt más adelante.
    new_user = User(email=email, password=password)
    
    # 5. Guardar en la base de datos
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'Usuario registrado exitosamente', 'user_id': new_user.id}), 201
    except Exception as e:
        db.session.rollback() # Deshacer cambios si hay error
        return jsonify({'message': str(e)}), 500

# --- RUTA 2: GUARDAR PERFIL AYURVÉDICO (Resultado del Test) ---
@api.route('/save_dosha', methods=['POST'])
def save_dosha():
    data = request.get_json()
    user_id = data.get('user_id')
    dominant_dosha = data.get('dominant_dosha')
    # Opcionales: puntajes
    vata = data.get('vata_score', 0)
    pitta = data.get('pitta_score', 0)
    kapha = data.get('kapha_score', 0)

    if not user_id or not dominant_dosha:
        return jsonify({'message': 'Faltan datos críticos (user_id o dosha)'}), 400

    try:
        # Verificar si el usuario ya tiene un perfil
        existing_profile = DoshaProfile.query.filter_by(user_id=user_id).first()

        if existing_profile:
            # Si existe, lo actualizamos
            existing_profile.dominant_dosha = dominant_dosha
            existing_profile.vata_score = vata
            existing_profile.pitta_score = pitta
            existing_profile.kapha_score = kapha
            message = "Perfil actualizado correctamente"
        else:
            # Si no existe, creamos uno nuevo
            new_profile = DoshaProfile(
                user_id=user_id,
                dominant_dosha=dominant_dosha,
                vata_score=vata,
                pitta_score=pitta,
                kapha_score=kapha
            )
            db.session.add(new_profile)
            message = "Perfil creado correctamente"
        
        db.session.commit()
        return jsonify({'message': message, 'dosha': dominant_dosha}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f"Error en base de datos: {str(e)}"}), 500
    
    # --- RUTA 3: INICIAR SESIÓN (LOGIN) ---
@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Faltan datos'}), 400

    # Buscar usuario en la base de datos
    user = User.query.filter_by(email=email).first()

    # Verificar si el usuario existe y si la contraseña coincide
    # NOTA: En producción, aquí usaríamos check_password_hash()
    if user and user.password == password:
        return jsonify({
            'message': 'Login exitoso',
            'user_id': user.id,
            'email': user.email
        }), 200
    else:
        return jsonify({'message': 'Credenciales inválidas'}), 401
    
    # --- RUTA 4: OBTENER DATOS DEL DASHBOARD ---
@api.route('/get_dashboard_data/<int:user_id>', methods=['GET'])
def get_dashboard_data(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'Usuario no encontrado'}), 404
            
        # Buscar su perfil de dosha
        profile = DoshaProfile.query.filter_by(user_id=user_id).first()
        
        dosha = "No definido"
        if profile:
            dosha = profile.dominant_dosha
            
        return jsonify({
            'email': user.email,
            'dosha': dosha,
            # Aquí podríamos enviar también el progreso de los hábitos
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
    # --- RUTA 5: REGISTRAR PROGRESO DIARIO ---
@api.route('/log_day', methods=['POST'])
def log_day():
    data = request.get_json()
    user_id = data.get('user_id')
    
    # Validamos que el usuario exista
    if not user_id:
        return jsonify({'message': 'Usuario no identificado'}), 400

    # Obtenemos la fecha de hoy (solo año-mes-día)
    today = dt.utcnow().date()

    try:
        # Verificar si ya existe un registro para HOY (para evitar duplicados)
        existing_log = DailyLog.query.filter_by(user_id=user_id, date=today).first()

        if existing_log:
            # Si ya existe, actualizamos los valores
            existing_log.slept_consistently = data.get('slept', existing_log.slept_consistently)
            existing_log.followed_diet = data.get('diet', existing_log.followed_diet)
            existing_log.mind_body_practice = data.get('meditation', existing_log.mind_body_practice)
            existing_log.movement = data.get('movement', existing_log.movement)
            existing_log.notes = data.get('notes', existing_log.notes)
            message = "Progreso de hoy actualizado"
        else:
            # Si no existe, creamos uno nuevo
            new_log = DailyLog(
                user_id=user_id,
                date=today,
                slept_consistently=data.get('slept', False),
                followed_diet=data.get('diet', False),
                mind_body_practice=data.get('meditation', False),
                movement=data.get('movement', False),
                notes=data.get('notes', '')
            )
            db.session.add(new_log)
            message = "Progreso registrado exitosamente"

        db.session.commit()
        return jsonify({'message': message}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500
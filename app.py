import os # <--- AGREGA ESTA LÍNEA AL PRINCIPIO
from flask import Flask, render_template, request, jsonify, send_from_directory
# ... resto de los imports ...
from flask import Flask, render_template
import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Importamos la instancia de la base de datos y los modelos
from backend.models import db, User, DoshaProfile, DailyLog
# Importamos el Blueprint de las rutas
from backend.routes import api # 👈 NUEVO: Importamos el objeto 'api' desde routes.py

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Inicializar la aplicación Flask
app = Flask(__name__)

# Configuración de la aplicación
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'clave_segura_por_defecto')
# Configuración de la Base de Datos (Inteligente)
# Si estamos en Render, usa la variable de entorno DATABASE_URL.
# Si estamos en tu computador local, usa el archivo sqlite:///tecnosia.db
database_url = os.environ.get('DATABASE_URL')

if database_url and database_url.startswith("postgres://"):
    # Corrección para SQLAlchemys antiguas que no entienden postgres://
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///tecnosia.db'

# Inicializar extensiones con la aplicación
db.init_app(app)
CORS(app)

# --- REGISTRAR BLUEPRINTS ---
# Aquí le decimos a Flask: "Usa las rutas que están definidas en el blueprint 'api'"
# url_prefix='/api' significa que todas esas rutas empezarán por /api
# Ejemplo: /api/register, /api/save_dosha
app.register_blueprint(api, url_prefix='/api') # 👈 NUEVO: Conectamos las rutas al servidor principal

# --- COMANDO PARA CREAR TABLAS (Solo desarrollo) ---
with app.app_context():
    try:
        db.create_all()
        # print("\n✅ Base de datos verificada.\n") # Comentado para que no sature la terminal
    except Exception as e:
        print(f"\n❌ Error con la base de datos: {e}\n")
        if 'unable to open database file' in str(e):
             print("💡 Creando carpeta 'instance'...")
             os.makedirs('instance', exist_ok=True)
             db.create_all()
             print("✅ Base de datos creada.\n")


# --- RUTA PRINCIPAL (FRONTEND) ---
@app.route('/')
def index():
    # Esto busca el archivo 'index.html' dentro de la carpeta 'templates'
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/test-dosha')
def test_dosha_page():
    return render_template('test_dosha.html')

# --- RUTA 4: DASHBOARD (PANEL DE CONTROL) ---
@app.route('/dashboard')
def dashboard_page():
    # Nota: En una app real, verificaríamos la sesión del usuario aquí.
    # Por ahora, el frontend se encargará de redirigir si no hay usuario.
    return render_template('dashboard.html')

# Iniciar el servidor de desarrollo
if __name__ == '__main__':
    # debug=True permite reiniciar el servidor automáticamente al guardar cambios
    print("\n🚀 Servidor iniciando en http://127.0.0.1:5000")
    print("📡 Rutas de API disponibles bajo /api/...\n")
    app.run(debug=True, port=5000)
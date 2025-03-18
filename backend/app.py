from flask import Flask, send_from_directory
from config import Config
from models import db
import os
import webbrowser
from routes import rtp_blueprint

STATIC_FOLDER = os.path.join(os.path.dirname(__file__), '../frontend')
app = Flask(__name__, static_folder=STATIC_FOLDER)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    # Para desarrollo: eliminar y recrear las tablas (temporal)
    db.drop_all()
    db.create_all()

# Servir index.html en la raíz
@app.route('/')
def home():
    return app.send_static_file('index.html')

# Servir archivos estáticos desde el directorio frontend
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

# Registrar el blueprint con todos los endpoints de RTP
app.register_blueprint(rtp_blueprint)

if __name__ == '__main__':
    webbrowser.open("http://127.0.0.1:5000/")
    app.run(debug=True)

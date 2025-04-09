from flask import Flask, send_from_directory
from config import Config
from models import db, Actor
import os
import webbrowser
from routes import rtp_blueprint

STATIC_FOLDER = os.path.join(os.path.dirname(__file__), '../frontend')
app = Flask(__name__, static_folder=STATIC_FOLDER)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.drop_all()
    db.create_all()

    # Crear los 4 usuarios predefinidos:
    # 1) "Mercadona" => beneficiary
    # 2) "PSPMercadona" => psp_beneficiary
    # 3) "PSPalonso" => psp_payer
    # 4) "alonso" => payer
    # Contraseñas ficticias, p.ej. "1234"
    mercadona = Actor(
        username="Mercadona",
        password="1234",
        name="Mercadona S.A.",
        role="beneficiary"
    )
    psp_merc = Actor(
        username="PSPMercadona",
        password="1234",
        name="PSP de Mercadona",
        role="psp_beneficiary"
    )
    psp_alonso = Actor(
        username="PSPalonso",
        password="1234",
        name="PSP de Alonso",
        role="psp_payer"
    )
    alonso = Actor(
        username="alonso",
        password="1234",
        name="Alonso",
        role="payer"
    )

    db.session.add_all([mercadona, psp_merc, psp_alonso, alonso])
    db.session.commit()

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

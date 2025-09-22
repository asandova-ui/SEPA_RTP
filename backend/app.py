from flask import Flask, send_from_directory
from ext_socketio import socketio, join_room
from config import Config
from models import db, Actor
import os
import webbrowser
from routes import rtp_blueprint
from typing import Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

STATIC_FOLDER = os.path.join(os.path.dirname(__file__), '../frontend')
app = Flask(__name__, static_folder=STATIC_FOLDER)
app.config.from_object(Config)
db.init_app(app)

# Inicialización de SocketIO
socketio.init_app(app, cors_allowed_origins="*")

with app.app_context():
    db.drop_all()
    db.create_all()
    logger.info("Database tables created successfully")

    # Create 4 predefined users with hashed passwords
    try:
        mercadona = Actor(
            username="e",
            name="Empresa",
            role="beneficiary",
            iban="ES26001234567890123456",
            balance=0.0
        )
        mercadona.set_password("1")

        psp_merc = Actor(
            username="pm",
            name="PSP de empresa",
            role="psp_beneficiary"
        )
        psp_merc.set_password("1")

        psp_alonso = Actor(
            username="pa",
            name="PSP de Alonso",
            role="psp_payer"
        )
        psp_alonso.set_password("1")

        alonso = Actor(
            username="a",
            name="Alonso",
            role="payer",
            iban="ES45098765432100000000",
            balance=1000.0
        )
        alonso.set_password("1")

        db.session.add_all([mercadona, psp_merc, psp_alonso, alonso])
        db.session.commit()
        logger.info("Default users created successfully")

        # Link actors to their PSPs
        mercadona.psp_id = psp_merc.id
        alonso.psp_id = psp_alonso.id
        db.session.commit()
        logger.info("PSP relationships established successfully")

    except Exception as e:
        logger.error(f"Error creating default data: {e}")
        db.session.rollback()

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

@socketio.on('join')
def handle_join(data):
    try:
        actor_id = data.get('actor_id')
        if not actor_id:
            logger.warning("Join attempt without actor_id")
            return
            
        actor = Actor.query.get(actor_id)
        if actor:
            room = f"{actor.role}_{actor_id}"
            join_room(room)
            logger.info(f"Actor {actor_id} ({actor.name}) joined room {room}")
        else:
            logger.warning(f"Join attempt with invalid actor_id: {actor_id}")
    except Exception as e:
        logger.error(f"Error handling join: {e}")

if __name__ == '__main__':
    try:
        webbrowser.open("http://127.0.0.1:5000/")
        socketio.run(app, debug=False, host='127.0.0.1', port=5000)
    except Exception as e:
        logger.error(f"Error starting application: {e}")

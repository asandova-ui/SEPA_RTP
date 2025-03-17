from flask import Flask, jsonify, request
from config import Config
from models import db, RTP, Log
import os
import webbrowser
from flask import Flask, send_from_directory

STATIC_FOLDER = os.path.join(os.path.dirname(__file__), '../frontend')
app = Flask(__name__, static_folder=STATIC_FOLDER)
app.config.from_object(Config)
db.init_app(app)


with app.app_context():
    db.drop_all()
    db.create_all() #temporal



# Define tus endpoints aquí

@app.route('/<path:filename>')
def serve_frontend_file(filename):
    return send_from_directory(app.static_folder, filename)


@app.route('/')
def home():
    return app.send_static_file('index.html')



@app.route('/rtp', methods=['POST'])
def crear_rtp():
    data = request.get_json()
    iban = data.get('iban')
    amount = data.get('amount')

    # Validaciones mínimas (por ejemplo, que no sean None)
    if not iban or not amount:
        return jsonify({"error": "Faltan campos requeridos"}), 400

    nuevo_rtp = RTP(iban=iban, amount=amount)
    db.session.add(nuevo_rtp)
    db.session.commit()

    return jsonify({"message": "RTP creado", "id": nuevo_rtp.id}), 201

@app.route('/rtp/<int:rtp_id>/validate', methods=['POST'])
def validar_rtp(rtp_id):
    rtp_obj = RTP.query.get(rtp_id)
    if not rtp_obj:
        return jsonify({"error": "RTP no encontrado"}), 404

    # Reglas de fraude básicas
    # 1. IBAN con formato "correcto" (simplificado)
    if len(rtp_obj.iban) < 15 or len(rtp_obj.iban) > 34:
        return rechazar_rtp(rtp_obj, "iban_invalido")

    # 2. Check repetición de IBAN + importe en los últimos X segundos
    #    (Pseudo-código: comprueba si hay otro RTP con mismo iban y amount y timestamp reciente)
    from datetime import datetime, timedelta
    hace_un_minuto = datetime.utcnow() - timedelta(seconds=60)
    duplicado = RTP.query.filter(
        RTP.iban == rtp_obj.iban,
        RTP.amount == rtp_obj.amount,
        RTP.timestamp >= hace_un_minuto,
        RTP.id != rtp_obj.id
    ).first()
    if duplicado:
        return rechazar_rtp(rtp_obj, "posible_fraude_repeticion")

    # Si pasa las reglas, actualizamos estado a 'validado'
    return cambiar_estado_rtp(rtp_obj, "validado")

@app.route('/rtp/<int:rtp_id>', methods=['PUT'])
def actualizar_rtp(rtp_id):
    data = request.get_json()
    new_status = data.get('new_status')
    rtp_obj = RTP.query.get(rtp_id)

    if not rtp_obj:
        return jsonify({"error": "RTP no encontrado"}), 404

    if new_status not in ["aceptado", "rechazado", "cancelado"]:
        return jsonify({"error": "Estado no válido"}), 400

    return cambiar_estado_rtp(rtp_obj, new_status)


@app.route('/logs', methods=['GET'])
def obtener_logs():
    logs = Log.query.all()
    resultado = []
    for log in logs:
        resultado.append({
            "id": log.id,
            "rtp_id": log.rtp_id,
            "old_status": log.old_status,
            "new_status": log.new_status,
            "timestamp": log.timestamp.isoformat(),
            "hash_value": log.hash_value
        })
    return jsonify(resultado)


import hashlib

def cambiar_estado_rtp(rtp_obj, new_status):
    old_status = rtp_obj.status
    rtp_obj.status = new_status
    db.session.commit()

    # Crear un hash simple con los datos clave
    # (Podrías incluir: id, iban, amount, old_status, new_status, timestamp, etc.)
    hash_input = f"{rtp_obj.id}{rtp_obj.iban}{rtp_obj.amount}{old_status}{new_status}".encode('utf-8')
    hash_value = hashlib.sha256(hash_input).hexdigest()

    nuevo_log = Log(
        rtp_id=rtp_obj.id,
        old_status=old_status,
        new_status=new_status,
        hash_value=hash_value
    )
    db.session.add(nuevo_log)
    db.session.commit()

    return jsonify({"message": f"RTP {rtp_obj.id} actualizado de {old_status} a {new_status}"}), 200

def rechazar_rtp(rtp_obj, motivo):
    # Podrías guardar 'motivo' en un campo extra si quisieras
    return cambiar_estado_rtp(rtp_obj, "rechazado")


if __name__ == '__main__':
    app.run(debug=True)

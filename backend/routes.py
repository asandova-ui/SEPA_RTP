from flask import Blueprint, request, jsonify
from services import (
    crear_rtp_service,
    validar_beneficiario_service,
    enrutar_rtp_service,
    validar_payer_service,
    decision_payer_service
)
from utils_roles import role_required
from models import Actor, db

rtp_blueprint = Blueprint('rtp', __name__)

# 1. Creación del RTP
@rtp_blueprint.route('/rtp', methods=['POST'])
@role_required('beneficiary')
def crear_rtp():
    data = request.get_json()
    result = crear_rtp_service(data)
    status = 201 if "error" not in result else 400
    return jsonify(result), status

# 2. Validación y Completar por el proveedor del beneficiario
@rtp_blueprint.route('/rtp/<int:rtp_id>/validate-beneficiary', methods=['POST'])
@role_required('psp_beneficiary')
def validar_beneficiario(rtp_id):
    result = validar_beneficiario_service(rtp_id)
    status = 200 if "error" not in result else 400
    return jsonify(result), status

# 3. Enrutamiento al proveedor del pagador
@rtp_blueprint.route('/rtp/<int:rtp_id>/route', methods=['POST'])
@role_required('psp_beneficiary')
def enrutar_rtp(rtp_id):
    result = enrutar_rtp_service(rtp_id)
    status = 200 if "error" not in result else 400
    return jsonify(result), status

# 4. Validación por el proveedor del pagador
@rtp_blueprint.route('/rtp/<int:rtp_id>/validate-payer', methods=['POST'])
@role_required('psp_payer')
def validar_payer(rtp_id):
    result = validar_payer_service(rtp_id)
    status = 200 if "error" not in result else 400
    return jsonify(result), status

# 5. Decisión final del pagador
@rtp_blueprint.route('/rtp/<int:rtp_id>/decision', methods=['POST'])
@role_required('payer')
def decision_payer(rtp_id):
    data = request.get_json()  # Esperamos un campo, por ejemplo, "decision": "aceptado" o "rechazado"
    result = decision_payer_service(rtp_id, data)
    status = 200 if "error" not in result else 400
    return jsonify(result), status

# Endpoint para obtener logs (opcional)
@rtp_blueprint.route('/logs', methods=['GET'])
def obtener_logs():
    # Implementa o reutiliza la lógica para listar logs
    # Por ejemplo, en services podrías tener una función obtener_logs_service()
    from models import Log
    logs = Log.query.all()
    result = [log.to_dict() for log in logs]
    return jsonify(result)


@rtp_blueprint.route('/actors', methods=['POST'])
def create_actor():
    data = request.get_json()
    name = data.get('name')
    role = data.get('role')  # 'beneficiary', 'psp_beneficiary', 'psp_payer', 'payer'

    if not name or not role:
        return jsonify({"error": "Faltan campos requeridos: name, role"}), 400

    # Validar que el role sea uno de los cuatro permitidos:
    valid_roles = ['beneficiary', 'psp_beneficiary', 'psp_payer', 'payer']
    if role not in valid_roles:
        return jsonify({"error": f"Rol '{role}' no válido"}), 400

    actor = Actor(name=name, role=role)
    db.session.add(actor)
    db.session.commit()

    return jsonify({"message": "Actor creado", "id": actor.id, "role": actor.role}), 201

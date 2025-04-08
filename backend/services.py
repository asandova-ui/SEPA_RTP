from models import db, RTP
from utils import cambiar_estado_rtp, rechazar_rtp, validar_iban

def crear_rtp_service(data, benef_id, psp_benef_id, psp_payer_id, payer_id):
    iban = data.get('iban')
    amount = data.get('amount')

    # Podrías validar que no sean None, etc.
    nuevo_rtp = RTP(
        iban=iban,
        amount=amount,
        beneficiary_id=benef_id,
        psp_beneficiary_id=psp_benef_id,
        psp_payer_id=psp_payer_id,
        payer_id=payer_id
    )
    db.session.add(nuevo_rtp)
    db.session.commit()
    return {"message": "RTP creado", "id": nuevo_rtp.id}

def validar_beneficiario_service(rtp_id):
    rtp_obj = RTP.query.get(rtp_id)
    if not rtp_obj:
        return {"error": "RTP no encontrado"}
    # Aquí podrías validar IBAN, etc.
    return cambiar_estado_rtp(db, rtp_obj, "validado-beneficiario")

def enrutar_rtp_service(rtp_id):
    rtp_obj = RTP.query.get(rtp_id)
    if not rtp_obj:
        return {"error": "RTP no encontrado"}
    return cambiar_estado_rtp(db, rtp_obj, "enrutado")

def validar_payer_service(rtp_id):
    rtp_obj = RTP.query.get(rtp_id)
    if not rtp_obj:
        return {"error": "RTP no encontrado"}
    return cambiar_estado_rtp(db, rtp_obj, "validado_payer")

def decision_payer_service(rtp_id, data):
    rtp_obj = RTP.query.get(rtp_id)
    if not rtp_obj:
        return {"error": "RTP no encontrado"}
    
    decision = data.get('decision')
    if decision not in ["aceptado", "rechazado"]:
        return {"error": "Decisión no válida"}
    
    return cambiar_estado_rtp(db, rtp_obj, decision)

from models import db, RTP
from utils import cambiar_estado_rtp, rechazar_rtp, validar_iban
from datetime import datetime, timedelta

def crear_rtp_service(data, benef_id, psp_benef_id, psp_payer_id, payer_id):
    iban = data.get('iban')
    amount = data.get('amount')

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
    """
    Validación inicial por el proveedor de servicios del beneficiario:
    - Verifica campos, formato, etc.
    - Si es correcto, añade información adicional y actualiza el estado a 'completado'
    """
    rtp_obj = RTP.query.get(rtp_id)
    if not rtp_obj:
        return {"error": "RTP no encontrado"}
    # Validación básica (puedes agregar más reglas aquí)
    
    #if not validar_iban(rtp_obj.iban):
    #   return rechazar_rtp(db, rtp_obj, "iban_invalido")

    # Simula el "validado-beneficiario": añade info adicional (ejemplo: marca de tiempo o identificador de enrutamiento)
    # Aquí podrías actualizar campos adicionales si los tuvieras.
    return cambiar_estado_rtp(db, rtp_obj, "validado-beneficiario")  # Estado 'completado' para indicar que se completó la info adicional

def enrutar_rtp_service(rtp_id):
    """
    Simula el enrutamiento del RTP al proveedor del pagador.
    En un sistema real, aquí se podría definir la lógica para seleccionar el endpoint del pagador.
    """
    rtp_obj = RTP.query.get(rtp_id)
    if not rtp_obj:
        return {"error": "RTP no encontrado"}
    # Actualiza el estado a 'enrutado'
    return cambiar_estado_rtp(db, rtp_obj, "enrutado")

def validar_payer_service(rtp_id):
    """
    Validación por el proveedor del pagador.
    Se pueden aplicar validaciones específicas o chequeos adicionales de fraude.
    """
    rtp_obj = RTP.query.get(rtp_id)
    #AQUI DEBE IR EL CONTROL DE FRAUDE
    if not rtp_obj:
        return {"error": "RTP no encontrado"}
    
    # Ejemplo de validación: si el RTP ya fue enrutado, se puede validar para enviarlo al pagador.
    # Aquí puedes agregar más validaciones.
    return cambiar_estado_rtp(db, rtp_obj, "validado_payer")

def decision_payer_service(rtp_id, data):
    """
    El pagador toma la decisión final.
    Se espera un campo "decision" en data con valores "aceptado" o "rechazado".
    """
    rtp_obj = RTP.query.get(rtp_id)
    if not rtp_obj:
        return {"error": "RTP no encontrado"}
    
    decision = data.get('decision')
    if decision not in ["aceptado", "rechazado"]:
        return {"error": "Decisión no válida"}
    
    return cambiar_estado_rtp(db, rtp_obj, decision)

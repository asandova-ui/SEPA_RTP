from models import db, RTP, Actor
from utils import cambiar_estado_rtp, rechazar_rtp, validar_iban

def crear_rtp_service(data):
    beneficiary_id = data.get('actor_id')
    payer_iban = data.get('payer_iban')
    amount = data.get('amount')

    # 1) Beneficiario
    beneficiary = Actor.query.get(beneficiary_id)
    if not beneficiary or beneficiary.role != 'beneficiary':
        return {"error": "El actor no es beneficiario o no existe"}

    # 2) PSP del Beneficiario
    if not beneficiary.psp_id:
        return {"error": "El beneficiario no tiene PSP asociado"}
    psp_benef_id = beneficiary.psp_id

    # 3) Hallar el pagador por su IBAN
    payer = Actor.query.filter_by(iban=payer_iban, role='payer').first()
    if not payer:
        return {"error": "No se encontró un pagador con ese IBAN"}

    # 4) PSP del pagador
    if not payer.psp_id:
        return {"error": "El pagador no tiene PSP asociado"}
    psp_payer_id = payer.psp_id

    # Crear el RTP
    nuevo_rtp = RTP(
        iban=payer_iban,
        amount=amount,
        beneficiary_id=beneficiary.id,
        psp_beneficiary_id=psp_benef_id,
        psp_payer_id=psp_payer_id,
        payer_id=payer.id
    )
    db.session.add(nuevo_rtp)
    db.session.commit()

    return {
        "message": "RTP creado correctamente",
        "id": nuevo_rtp.id,
        "beneficiary_id": beneficiary.id,
        "psp_beneficiary_id": psp_benef_id,
        "payer_id": payer.id,
        "psp_payer_id": psp_payer_id
    }

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
    """
    Validación por el PSP del pagador.
    1) Si el payer no tiene saldo suficiente, forzamos 'rechazado' (o 'cancelado')
    2) Si sí tiene saldo, seguimos con 'validado_payer'
    """
    rtp_obj = RTP.query.get(rtp_id)
    if not rtp_obj:
        return {"error": "RTP no encontrado"}

    # Busco el Actor que sea el payer:
    from models import Actor
    payer_actor = Actor.query.get(rtp_obj.payer_id)
    if not payer_actor:
        return {"error": "El payer asignado a este RTP no existe"}

    # Verifico fondos
    if payer_actor.balance < rtp_obj.amount:
        # Forzamos el rechazo
        return rechazar_rtp(db, rtp_obj, "Saldo insuficiente (PSP forzó cancelación)")

    # Si hay saldo suficiente, marcamos 'validado_payer'
    return cambiar_estado_rtp(db, rtp_obj, "validado_payer")


def decision_payer_service(rtp_id, data):
    """
    Cuando el pagador da su decisión final ('aceptado' o 'rechazado')
    1) Si 'aceptado', restamos el dinero de su cuenta.
    """
    rtp_obj = RTP.query.get(rtp_id)
    if not rtp_obj:
        return {"error": "RTP no encontrado"}
    
    decision = data.get('decision')
    if decision not in ["aceptado", "rechazado"]:
        return {"error": "Decisión no válida"}

    # Si es 'aceptado', restamos el dinero
    if decision == "aceptado":
        from models import Actor
        payer_actor = Actor.query.get(rtp_obj.payer_id)
        if not payer_actor:
            return {"error": "El payer asignado no existe"}

        # Ya pasamos la validación en el PSP, así que se asume que hay saldo.
        # Pero revisamos por seguridad:
        if payer_actor.balance < rtp_obj.amount:
            # Fuerzo un rechazo
            return rechazar_rtp(db, rtp_obj, "Saldo insuficiente en el último momento")

        # Resto
        payer_actor.balance -= rtp_obj.amount
        db.session.commit()

    return cambiar_estado_rtp(db, rtp_obj, decision)

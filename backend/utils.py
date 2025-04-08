import hashlib
from models import Log

def cambiar_estado_rtp(db, rtp_obj, new_status):
    old_status = rtp_obj.status
    rtp_obj.status = new_status
    db.session.commit()

    # Generar un hash
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

    return {
        "message": f"RTP {rtp_obj.id} actualizado de {old_status} a {new_status}"
    }

def rechazar_rtp(db, rtp_obj, motivo):
    return cambiar_estado_rtp(db, rtp_obj, "rechazado")

def validar_iban(iban):
    # Aquí tu implementación de validación IBAN si la necesitas
    return True

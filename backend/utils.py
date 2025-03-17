# utils.py
import hashlib

def cambiar_estado_rtp(rtp_obj, new_status, db, Log):
    old_status = rtp_obj.status
    rtp_obj.status = new_status
    db.session.commit()

    # Crear un hash simple con los datos clave
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

    return {"message": f"RTP {rtp_obj.id} actualizado de {old_status} a {new_status}"}

def rechazar_rtp(rtp_obj, motivo, db, Log):
    # Puedes incorporar el motivo en el registro o manejarlo de otra forma
    return cambiar_estado_rtp(rtp_obj, "rechazado", db, Log)

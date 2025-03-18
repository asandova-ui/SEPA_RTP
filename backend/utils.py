import hashlib
from flask import jsonify
from models import Log

def cambiar_estado_rtp(db, rtp_obj, new_status):
    """
    Cambia el estado del RTP y registra el cambio.
    """
    old_status = rtp_obj.status
    rtp_obj.status = new_status
    db.session.commit()

    # Generar un hash simple con los datos clave
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
    """
    Rechaza el RTP (actualizando su estado a 'rechazado') y registra el cambio.
    """
    return cambiar_estado_rtp(db, rtp_obj, "rechazado")

def validar_iban(iban):
    # Eliminar espacios y convertir a mayúsculas
    iban = iban.replace(" ", "").upper()

    # Verificar longitud del IBAN (cada país tiene una longitud distinta)
    paises_longitudes = {
        'AL': 28, 'AD': 24, 'AT': 20, 'AZ': 28, 'BH': 22, 'BE': 16, 'BA': 20, 'BR': 29,
        'BG': 22, 'CR': 22, 'HR': 21, 'CY': 28, 'CZ': 24, 'DK': 18, 'DO': 28, 'EE': 20,
        'FO': 18, 'FI': 18, 'FR': 27, 'DE': 22, 'GI': 23, 'GR': 27, 'GL': 18, 'GT': 28,
        'HU': 28, 'IS': 26, 'IE': 22, 'IL': 23, 'IT': 27, 'KW': 30, 'LV': 21, 'LB': 28,
        'LI': 21, 'LT': 20, 'LU': 20, 'MK': 19, 'MT': 31, 'MR': 27, 'MU': 30, 'MD': 24,
        'MC': 27, 'ME': 22, 'NL': 20, 'NO': 15, 'PK': 24, 'PL': 28, 'PT': 25, 'QA': 29,
        'RO': 24, 'RS': 22, 'SM': 27, 'SA': 24, 'SE': 24, 'CH': 21, 'TR': 26, 'TN': 24,
        'UA': 29, 'GB': 22, 'VG': 24, 'ES': 24  # España añadida
    }

    pais = iban[:2]
    if pais not in paises_longitudes or len(iban) != paises_longitudes[pais]:
        return False  # Longitud incorrecta

    # Reorganizar el IBAN (mover los primeros 4 caracteres al final)
    iban_reorganizado = iban[4:] + iban[:4]

    # Convertir las letras en números
    iban_numerico = ""
    for char in iban_reorganizado:
        if char.isdigit():
            iban_numerico += char
        elif char.isalpha():
            iban_numerico += str(ord(char) - 55)  # Convertir letra a número (A=10, B=11, ..., Z=35)
        else:
            return False  # Caracter no válido

    # Verificar si el número es divisible por 97
    if int(iban_numerico) % 97 == 1:
        return True
    else:
        return False

import hashlib
import string
import re
from typing import Optional, Dict, Any
from models import Log
import logging

logger = logging.getLogger(__name__)

def cambiar_estado_rtp(db, rtp_obj, new_status: str) -> Dict[str, Any]:
    """
    Change RTP status and log the change with hash for traceability.
    
    Args:
        db: Database session
        rtp_obj: RTP object to update
        new_status: New status to set
        
    Returns:
        Dict with result message
    """
    try:
        old_status = rtp_obj.status
        rtp_obj.status = new_status
        db.session.commit()

        # Generate hash for traceability
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
        
        logger.info(f"RTP {rtp_obj.id} status changed from {old_status} to {new_status}")

        return {
            "message": f"RTP {rtp_obj.id} updated from {old_status} to {new_status}",
            "hash": hash_value
        }
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error changing RTP status: {e}")
        raise

def rechazar_rtp(db, rtp_obj, motivo: str) -> Dict[str, Any]:
    """Reject an RTP with reason."""
    logger.info(f"Rejecting RTP {rtp_obj.id} - Reason: {motivo}")
    return cambiar_estado_rtp(db, rtp_obj, "rechazado")

def validar_iban(iban: str) -> bool:
    """
    Valida un IBAN (ISO 13616) usando el algoritmo de
    “módulo 97 = 1”.

    Parámetros
    ----------
    iban : str
        IBAN en cualquier formato (con o sin espacios).

    Retorna
    -------
    bool
        True si el IBAN es sintácticamente correcto, False en caso contrario.
    """
    if not iban:
        return False

    # 1) Limpiar y normalizar
    iban = iban.replace(" ", "").upper()
    if len(iban) < 15 or len(iban) > 34 or not iban.isalnum():
        return False

    # 2) Reorganizar: los cuatro primeros caracteres al final
    rearranged = iban[4:] + iban[:4]

    # 3) Convertir letras a números (A=10, B=11, …, Z=35)
    digits = []
    for ch in rearranged:
        if ch.isdigit():
            digits.append(ch)
        elif ch.isalpha():
            digits.append(str(10 + string.ascii_uppercase.index(ch)))
        else:
            return False
    numeric_iban = int("".join(digits))

    # 4) Comprobar resto
    return numeric_iban % 97 == 1


def sanitize_input(value: str, max_length: int = 255) -> str:
    """Sanitize string input to prevent basic injection attacks."""
    if not isinstance(value, str):
        return ""
    
    # Remove potential dangerous characters
    sanitized = re.sub(r'[<>"\';\\]', '', value)
    return sanitized[:max_length].strip()

def validate_amount(amount: Any) -> Optional[float]:
    """Validate and convert amount to float."""
    try:
        amount_float = float(amount)
        if amount_float <= 0:
            return None
        if amount_float > 999999.99:  # Reasonable limit
            return None
        return round(amount_float, 2)
    except (ValueError, TypeError):
        return None


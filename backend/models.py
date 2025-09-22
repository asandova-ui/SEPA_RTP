from flask_sqlalchemy import SQLAlchemy
from typing import Optional, Dict, Any
try:
    import bcrypt
except ImportError:
    import hashlib
    bcrypt = None

db = SQLAlchemy()

class Actor(db.Model):
    __tablename__ = 'actor'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)  # Changed from password to password_hash
    name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    photo_url = db.Column(db.String(200), nullable=True)
    iban = db.Column(db.String(34), nullable=True)
    balance = db.Column(db.Float, default=0.0)

    # Campo para PSP association
    psp_id = db.Column(db.Integer, db.ForeignKey('actor.id'), nullable=True)
    psp = db.relationship('Actor', remote_side=[id])

    def set_password(self, password: str) -> None:
        """Hash and set the password."""
        if bcrypt:
            self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        else:
            # Fallback to simple hashing (not secure for production)
            self.password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash."""
        if bcrypt:
            return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
        else:
            # Fallback for simple hash
            return self.password_hash == hashlib.sha256(password.encode('utf-8')).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "role": self.role,
            "photo_url": self.photo_url,
            "iban": self.iban,
            "balance": self.balance,
            "psp_id": self.psp_id
        }

class RTP(db.Model):
    __tablename__ = 'rtp'
    id = db.Column(db.Integer, primary_key=True)
    iban = db.Column(db.String(34), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="creado", nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    beneficiary_id = db.Column(db.Integer, nullable=False)
    psp_beneficiary_id = db.Column(db.Integer, nullable=False)
    psp_payer_id = db.Column(db.Integer, nullable=False)
    payer_id = db.Column(db.Integer, nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "iban": self.iban,
            "amount": self.amount,
            "status": self.status,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "beneficiary_id": self.beneficiary_id,
            "psp_beneficiary_id": self.psp_beneficiary_id,
            "psp_payer_id": self.psp_payer_id,
            "payer_id": self.payer_id
        }

class Log(db.Model):
    __tablename__ = 'log'
    id = db.Column(db.Integer, primary_key=True)
    rtp_id = db.Column(db.Integer, nullable=False)
    old_status = db.Column(db.String(20))
    new_status = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    hash_value = db.Column(db.String(64))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "rtp_id": self.rtp_id,
            "old_status": self.old_status,
            "new_status": self.new_status,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "hash_value": self.hash_value
        }

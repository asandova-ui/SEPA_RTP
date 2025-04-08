from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class RTP(db.Model):
    __tablename__ = 'rtp'
    id = db.Column(db.Integer, primary_key=True)
    iban = db.Column(db.String(34), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="creado")
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            "id": self.id,
            "iban": self.iban,
            "amount": self.amount,
            "status": self.status,
            "timestamp": self.timestamp.isoformat()
        }

class Log(db.Model):
    __tablename__ = 'log'
    id = db.Column(db.Integer, primary_key=True)
    rtp_id = db.Column(db.Integer, nullable=False)
    old_status = db.Column(db.String(20))
    new_status = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    hash_value = db.Column(db.String(64))

    def to_dict(self):
        return {
            "id": self.id,
            "rtp_id": self.rtp_id,
            "old_status": self.old_status,
            "new_status": self.new_status,
            "timestamp": self.timestamp.isoformat(),
            "hash_value": self.hash_value
        }

class Actor(db.Model):
    __tablename__ = 'actor'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)   # Nombre del actor
    role = db.Column(db.String(20), nullable=False)   # Ej: 'beneficiary', 'psp_beneficiary', 'psp_payer', 'payer'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role
        }
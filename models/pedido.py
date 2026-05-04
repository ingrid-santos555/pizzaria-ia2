from database.db import db
from datetime import datetime
import uuid

class Pedido(db.Model):
    __tablename__ = "pedido"  # 🔥 ESSENCIAL

    id = db.Column(db.Integer, primary_key=True)

    nome_cliente = db.Column(db.String(100))
    endereco = db.Column(db.String(100))
    sabor = db.Column(db.String(100))
    tamanho = db.Column(db.String(50))
    quantidade = db.Column(db.Integer)
    valor_total = db.Column(db.Float)

    status = db.Column(db.String(50), default="novo")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔐 TOKEN SEGURO
    token = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4())
    )
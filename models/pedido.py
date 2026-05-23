from database.db import db
from datetime import datetime
import uuid
import json


class Pedido(db.Model):
    __tablename__ = "pedido"

    id = db.Column(db.Integer, primary_key=True)

    nome_cliente = db.Column(db.String(100))
    endereco = db.Column(db.String(100))

    # AGORA SUPORTA:
    # [
    #   {
    #      "sabores": ["calabresa", "frango"],
    #      "quantidade": 1,
    #      "tamanho": "grande"
    #   }
    # ]
    itens = db.Column(db.Text)

    valor_total = db.Column(db.Float)

    status = db.Column(db.String(50), default="novo")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    token = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4())
    )

    # AUXILIAR PARA SALVAR JSON
    def set_itens(self, itens_list):
        self.itens = json.dumps(itens_list)

    # AUXILIAR PARA LER JSON
    def get_itens(self):
        return json.loads(self.itens or "[]")
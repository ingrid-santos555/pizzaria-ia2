from database.db import db

class Usuario(db.Model):
    __tablename__ = "usuario"  # 🔥 ADICIONA ISSO

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    username = db.Column(db.String(50), unique=True)
    telefone = db.Column(db.String(20))
    senha = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)
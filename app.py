import os
import unicodedata
import secrets

from flask import Flask, request, jsonify, render_template, session, redirect
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config
from database.db import db
from models.pedido import Pedido
from models.usuarios import Usuario  

from crew.crew_setup import run_crew
from crew.tools import CARDAPIO


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret")
app.config.from_object(Config)

db.init_app(app)


# ========================
# 🔥 CRIA BANCO + ADMIN
# ========================
with app.app_context():
    db.create_all()

    admin = Usuario.query.filter_by(username="admin").first()

    if not admin:
        print("🔥 Criando admin...")
        admin = Usuario(
            nome="Administrador",
            username="admin",
            telefone="000000000",
            senha=generate_password_hash("147888"),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
    else:
        print("🔥 Atualizando senha do admin...")
        admin.senha = generate_password_hash("147888")
        db.session.commit()


MAX_HISTORICO = 10
TAXA_ENTREGA = 15


# ========================
# 🔧 FUNÇÕES AUXILIARES
# ========================

def gerar_token():
    return secrets.token_urlsafe(16)


def normalizar_tamanho(texto):
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    return texto


def calcular_valor(tamanho, quantidade):
    preco = CARDAPIO["tamanhos"].get(tamanho, 0)
    subtotal = preco * quantidade
    total = subtotal + TAXA_ENTREGA
    return subtotal, total


# ========================
# 🟢 PÁGINAS
# ========================

@app.route("/")
def home():
    return render_template("pagina_inicial.html")


@app.route("/pedido")
def pedido():
    return render_template("atendente.html")


@app.route("/sobre")
def sobre():
    return render_template("sobre_nos.html")


@app.route("/contato")
def contato():
    return render_template("contato.html")


@app.route("/login-page")
def login_page():
    return render_template("login.html")


@app.route("/index")
def index():
    if not session.get("user_id"):
        return redirect("/login-page")

    return render_template(
        "index.html",
        is_admin=session.get("is_admin", False)
    )


@app.route("/painel")
def painel():
    if not session.get("user_id"):
        return redirect("/login-page")

    return render_template("painel_gerenciamento.html")

@app.route("/historico")
def historico():
    if not session.get("user_id"):
        return redirect("/login-page")

    return render_template("historico_tabela.html")

# 🔒 PROTEÇÃO REAL DE ADMIN
@app.route("/formulario")
def formulario():
    user_id = session.get("user_id")

    if not user_id:
        return "Acesso negado", 403

    user = Usuario.query.get(user_id)

    if not user or user.is_admin is not True:
        return "Acesso negado", 403

    return render_template("formulario.html")


@app.route("/acompanhar/<token>")
def acompanhar(token):
    return render_template("acompanhar.html")


# ========================
# 🟢 CHAT
# ========================

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    mensagem = data.get("message", "").strip()

    if not mensagem:
        return jsonify({"reply": "Digite uma mensagem válida."})

    if "historico" not in session:
        session["historico"] = []

    # 🧑 usuário fala
    session["historico"].append({
        "role": "user",
        "content": mensagem
    })
    session.modified = True

    # limitar histórico
    if len(session["historico"]) > MAX_HISTORICO:
        session["historico"] = session["historico"][-MAX_HISTORICO:]

    try:
        resposta = run_crew(session["historico"])
    except Exception as e:
        print("Erro IA:", e)
        return jsonify({"reply": "Estamos processando seu pedido... 🍕"})

    # 🧠 CASO 1: resposta normal (texto)
    if not isinstance(resposta, dict):
        session["historico"].append({
            "role": "assistant",
            "content": str(resposta)
        })
        session.modified = True
        return jsonify({"reply": resposta})

    # 🧠 CASO 2: resposta estruturada (pedido completo)
    dados = resposta

    try:
        subtotal, valor_total = calcular_valor(
            normalizar_tamanho(dados["tamanho"]),
            int(dados["quantidade"])
        )
    except:
        return jsonify({"reply": "Erro ao processar pedido."})

    token = gerar_token()

    novo_pedido = Pedido(
        nome_cliente=dados["nome_completo"],
        endereco=dados["endereco"],
        sabor=dados["sabor"],
        tamanho=normalizar_tamanho(dados["tamanho"]),
        quantidade=int(dados["quantidade"]),
        valor_total=valor_total,
        status="novo",
        token=token
    )

    db.session.add(novo_pedido)
    db.session.commit()

    # 🧹 limpa histórico após finalizar pedido
    session.pop("historico", None)
    session.modified = True

    link = f"/pedido/{token}"

    return jsonify({
    "reply": (
        f"Pedido confirmado! 🍕\n\n"
        f"🧾 {dados['quantidade']}x pizza de {dados['sabor']} ({normalizar_tamanho(dados['tamanho'])})\n"
        f"📍 {dados['endereco']}\n"
        f"💰 Total: R$ {valor_total:.2f}\n\n"
        f"👉 Acompanhe seu pedido: /acompanhar/{token}"
    )
})


# ========================
# 🟡 PEDIDOS
# ========================

@app.route("/pedidos")
def listar_pedidos():
    pedidos = Pedido.query.order_by(Pedido.id.desc()).all()

    return jsonify([
        {
            "id": p.id,
            "nome_cliente": p.nome_cliente,
            "endereco": p.endereco,
            "sabor": p.sabor,
            "tamanho": p.tamanho,
            "quantidade": p.quantidade,
            "valor_total": p.valor_total,
            "status": p.status,
            "created_at": p.created_at.strftime("%d/%m/%Y %H:%M") if p.created_at else "",
            "created_at_iso": p.created_at.isoformat() if p.created_at else None,
        }
        for p in pedidos
    ])


@app.route("/pedidos/<int:id>/status", methods=["PUT"])
def atualizar_status(id):
    pedido = Pedido.query.get(id)

    if not pedido:
        return jsonify({"error": "Pedido não encontrado"}), 404

    pedido.status = request.json.get("status")
    db.session.commit()

    return jsonify({"msg": "ok"})


# ========================
# 🔐 REGISTRO
# ========================

@app.route("/usuarios", methods=["POST"])
def criar_usuario():
    data = request.json or request.form

    nome = data.get("nome")
    username = data.get("username")
    telefone = data.get("telefone")
    senha = data.get("senha")

    if not nome or not username or not senha:
        return jsonify({"error": "Dados incompletos"}), 400

    existente = Usuario.query.filter_by(username=username).first()
    if existente:
        return jsonify({"error": "Usuário já existe"}), 400

    novo_usuario = Usuario(
        nome=nome,
        username=username,
        telefone=telefone,
        senha=generate_password_hash(senha)
    )

    # 🔥 força segurança
    novo_usuario.is_admin = False

    db.session.add(novo_usuario)
    db.session.commit()

    return jsonify({"msg": "Usuário criado com sucesso"})


# ========================
# 🔐 LOGIN / LOGOUT
# ========================

@app.route("/login", methods=["POST"])
def login():
    session.clear()  # 🔥 limpa sessão antiga

    data = request.json or {}

    username = data.get("username")
    senha = data.get("senha")

    user = Usuario.query.filter_by(username=username).first()

    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 401

    if not check_password_hash(user.senha, senha):
        return jsonify({"error": "Senha incorreta"}), 401

    session["user_id"] = user.id
    session["is_admin"] = bool(user.is_admin)

    print("LOGIN:", user.username, user.is_admin)

    return jsonify({"msg": "ok"})


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ========================
# 🔗 ACOMPANHAMENTO
# ========================

@app.route("/pedido/<token>")
def get_pedido(token):
    pedido = Pedido.query.filter_by(token=token).first()

    if not pedido:
        return jsonify({"error": "Pedido não encontrado"}), 404

    return jsonify({
        "status": pedido.status,
        "sabor": pedido.sabor,
        "tamanho": pedido.tamanho,
        "quantidade": pedido.quantidade,
        "created_at": pedido.created_at.isoformat() if pedido.created_at else None
    })


@app.route("/pedido/<token>/cancelar", methods=["POST"])
def cancelar_pedido(token):
    pedido = Pedido.query.filter_by(token=token).first()

    if not pedido:
        return jsonify({"error": "Pedido não encontrado"}), 404

    pedido.status = "cancelado"
    db.session.commit()

    return jsonify({"msg": "cancelado"})


# ========================
# 🚀 START
# ========================

if __name__ == "__main__":
    app.run(debug=True)
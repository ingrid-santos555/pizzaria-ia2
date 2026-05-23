import os
import json

from dotenv import load_dotenv
from crewai import Crew, Process, LLM

from crew.agents import coletor_pedido_agent
from crew.tasks import coletar_pedido_task
from crew.tools import CARDAPIO

load_dotenv()

llm = LLM(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)


def formatar_historico(historico):
    linhas = []
    for msg in historico:
        if msg["role"] == "user":
            linhas.append(f"Usuário: {msg['content']}")
        else:
            linhas.append(f"Assistente: {msg['content']}")
    return "\n".join(linhas)


def run_crew(historico):
    historico_texto = formatar_historico(historico)

    agente = coletor_pedido_agent(llm)
    task = coletar_pedido_task(agente, historico_texto, CARDAPIO)  # ✅ passa direto
    crew = Crew(
        agents=[agente],
        tasks=[task],
        process=Process.sequential,
        verbose=False,
        memory=False
    )

    resultado = crew.kickoff()  # ✅ sem inputs

    resposta_raw = str(resultado).strip()  # ✅ 0.10.0 retorna string, não .raw
    resposta_raw = resposta_raw.replace("```json", "").replace("```", "").strip()

    try:
        dados = json.loads(resposta_raw)
        if isinstance(dados, dict):
            return dados
    except json.JSONDecodeError:
        pass

    return resposta_raw
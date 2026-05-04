from crewai import Task


def coletar_pedido_task(agent, historico_conversa, cardapio):
    return Task(
        description=f"""
Você receberá o histórico de uma conversa entre cliente e atendente de pizzaria.

Histórico da conversa:
{historico_conversa}

Cardápio disponível:
{cardapio}

Sua tarefa é continuar o atendimento.

PASSOS

1. Analise cuidadosamente todo o histórico da conversa.
2. Identifique quais informações do pedido já foram fornecidas pelo cliente.
3. Determine quais informações ainda faltam.

INFORMAÇÕES NECESSÁRIAS DO PEDIDO

- nome_completo
- endereco
- sabor
- tamanho
- quantidade

COMPORTAMENTO

Se ainda faltar alguma informação:
- Faça apenas UMA pergunta clara ao cliente.

Se todas as informações já estiverem disponíveis:
- Gere apenas o JSON final do pedido.

REGRAS

- Nunca invente informações.
- Nunca invente sabores que não estejam no cardápio.
- Nunca escreva explicações.
- O sabor do pedido é SEMPRE o último sabor mencionado pelo cliente.
- Nunca combine sabores de mensagens diferentes a menos que o cliente tenha pedido explicitamente.
- Nunca gere texto junto com o JSON.
""",
        agent=agent,
        expected_output="Uma pergunta clara ao cliente ou um JSON válido contendo o pedido completo."
    )
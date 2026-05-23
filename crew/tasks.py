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
- itens (cada item com: sabores, tamanho, quantidade)

COMPORTAMENTO

Se ainda faltar alguma informação:
- Faça apenas UMA pergunta clara ao cliente.

Se todas as informações já estiverem disponíveis:
- Gere apenas o JSON final do pedido.

REGRAS

- Nunca invente informações.
- Nunca invente sabores que não estejam no cardápio.
- Nunca escreva explicações.
- Capture todos os sabores mencionados para o mesmo item.
- "meia calabresa meia frango" = um item com sabores ["calabresa", "frango"].
- Itens diferentes são objetos separados na lista.
- Cada item do pedido deve ter seu próprio tamanho confirmado pelo cliente.
- Nunca assuma que todos os itens têm o mesmo tamanho.
- Se houver múltiplos itens e o tamanho de algum não foi informado, pergunte um por vez.
- Nunca gere texto junto com o JSON.
""",
        agent=agent,
        expected_output="Uma pergunta clara ao cliente ou um JSON válido contendo o pedido completo."
    )
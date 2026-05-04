let orders = [];

// 🔥 persistência dos ocultos
let ocultos = JSON.parse(localStorage.getItem("ocultos")) || [];


// 🔄 BUSCAR DO BACKEND
async function carregarPedidos() {
    try {
        const res = await fetch("/pedidos");
        const data = await res.json();
        orders = data;
        render();
    } catch (err) {
        console.error("Erro ao carregar pedidos:", err);
    }
}


// 🔢 CONTADOR POR STATUS (considera apenas visíveis)
function getCount(status) {
    return orders
        .filter(o => o.status === status && !ocultos.includes(o.id))
        .length;
}


// 🔁 PRÓXIMO STATUS
function nextStatus(status) {
    if (status === "novo") return "preparo";
    if (status === "preparo") return "entrega";
    if (status === "entrega") return "entregue";
    return null;
}


// 🚀 AVANÇAR PEDIDO (COM BACKEND)
async function moveOrder(id) {
    const order = orders.find(o => o.id === id);
    const next = nextStatus(order.status);

    if (!next) return;

    if (getCount(next) >= 4) {
        alert("Limite de 4 nessa coluna!");
        return;
    }

    try {
        await fetch(`/pedidos/${id}/status`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status: next })
        });

        carregarPedidos();
    } catch (err) {
        console.error("Erro ao atualizar status:", err);
    }
}


// 🗑 EXCLUIR (APENAS FRONT, AGORA PERSISTENTE)
function deleteFromView(id) {
    if (!ocultos.includes(id)) {
        ocultos.push(id);
        localStorage.setItem("ocultos", JSON.stringify(ocultos));
    }
    render();
}


// 🔄 OPCIONAL: limpar todos ocultos
function limparOcultos() {
    ocultos = [];
    localStorage.removeItem("ocultos");
    render();
}


// 🎨 RENDER
function render() {
    ["novo", "preparo", "entrega", "entregue"].forEach(s => {
        document.getElementById(s).innerHTML = "";
    });

    orders
        .filter(order => !ocultos.includes(order.id))
        .forEach(order => {

            const div = document.createElement("div");
            div.className = `card ${order.status}`;

            div.innerHTML = `
                <b>${order.nome_cliente}</b><br>
                End: ${order.endereco}<br>
                Pedido: ${order.sabor} (${order.tamanho})<br>
                Qtd: ${order.quantidade}<br>
                Valor: R$ ${order.valor_total}<br>
                Data: ${order.created_at}<br>
            `;

            // ▶️ AVANÇAR
            if (order.status !== "entregue") {
                const btn = document.createElement("button");
                btn.innerText = "Avançar";
                btn.onclick = () => moveOrder(order.id);
                div.appendChild(btn);
            }

            // 🗑 EXCLUIR (somente entregue)
            if (order.status === "entregue") {
                const deleteBtn = document.createElement("button");
                deleteBtn.innerText = "Excluir";
                deleteBtn.onclick = () => deleteFromView(order.id);
                div.appendChild(deleteBtn);
            }

            // ✅ ignora pedidos com status sem coluna (ex: cancelado)
            const coluna = document.getElementById(order.status);
            if (coluna) coluna.appendChild(div);
        });
}


// 🚀 INICIALIZAÇÃO
carregarPedidos();

// 🔄 AUTO UPDATE
setInterval(carregarPedidos, 3000);
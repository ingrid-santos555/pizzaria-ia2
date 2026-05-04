let pedidos = [];

// 🔄 BUSCAR DO BACKEND
async function carregarTabela() {
    const res = await fetch("/pedidos");
    pedidos = await res.json();

    renderTabela();
}

// 🎨 RENDER
function renderTabela() {
    const tbody = document.querySelector("#tabela tbody");
    tbody.innerHTML = "";

    pedidos.forEach(p => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${p.nome_cliente}</td>
            <td>${p.endereco}</td>
            <td>${p.sabor}</td>
            <td>${p.tamanho}</td>
            <td>${p.quantidade}</td>
            <td>R$ ${p.valor_total}</td>
            <td>${p.status}</td>
            <td>${p.created_at}</td>
        `;

        tbody.appendChild(tr);
    });
}

// 📥 CSV CORRIGIDO (EXCEL PT-BR)
function baixarCSV(tipo) {
    let dados = pedidos;
    const hoje = new Date();

    if (tipo === "semana") {
        dados = pedidos.filter(p =>
            new Date(p.created_at) >= new Date(hoje - 7 * 24 * 60 * 60 * 1000)
        );
    }

    if (tipo === "mes") {
        dados = pedidos.filter(p =>
            new Date(p.created_at) >= new Date(hoje - 30 * 24 * 60 * 60 * 1000)
        );
    }

    if (tipo === "ano") {
        dados = pedidos.filter(p =>
            new Date(p.created_at) >= new Date(hoje - 365 * 24 * 60 * 60 * 1000)
        );
    }

    // ✅ separador correto pro Excel
    let csv = "Cliente;Endereco;Sabor;Tamanho;Quantidade;Valor;Status;Data\n";

    dados.forEach(p => {
        csv += `"${p.nome_cliente}";"${p.endereco}";"${p.sabor}";"${p.tamanho}";"${p.quantidade}";"${p.valor_total}";"${p.status}";"${p.created_at}"\n`;
    });

    // ✅ resolve problema de acento no Excel
    const blob = new Blob(["\ufeff" + csv], {
        type: "text/csv;charset=utf-8;"
    });

    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "historico.csv";
    a.click();
}

// 🚀 INICIAR
carregarTabela();
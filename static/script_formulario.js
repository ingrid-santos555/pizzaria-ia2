document.querySelector("form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const form = e.target;
    const btn = form.querySelector("input[type='submit']");

    btn.disabled = true;
    btn.value = "Registrando...";

    try {
        const nome = form.nome.value.trim();
        const username = form.username.value.trim();
        const telefone = form.telefone.value.trim();
        const senha = form.senha.value;
        const confirmar = form.confirmar.value;

        // 🔒 validação
        if (!nome || !username || !telefone || !senha || !confirmar) {
            alert("Preencha todos os campos");
            return;
        }

        if (senha.length < 4) {
            alert("A senha deve ter pelo menos 4 caracteres");
            return;
        }

        if (senha !== confirmar) {
            alert("As senhas não coincidem");
            return;
        }

        const res = await fetch("/usuarios", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                nome,
                username,
                telefone,
                senha
            })
        });

        // 🔥 evita erro se backend não retornar JSON
        let data = {};
        try {
            data = await res.json();
        } catch {
            data = {};
        }

        if (!res.ok) {
            alert(data.error || "Erro ao criar usuário");
            return;
        }

        alert("Usuário criado com sucesso!");

        // limpa
        form.reset();

        // redireciona
        window.location.href = "/index";

    } catch (err) {
        console.error("Erro no cadastro:", err);
        alert("Erro inesperado ao conectar com o servidor");
    } finally {
        btn.disabled = false;
        btn.value = "Registrar";
    }
});
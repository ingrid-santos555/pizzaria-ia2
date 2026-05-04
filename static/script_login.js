document.querySelector(".login").addEventListener("click", async () => {

    const username = document.querySelector("input[placeholder='Usuário']").value;
    const senha = document.querySelector("input[placeholder='Senha']").value;

    const res = await fetch("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, senha })
    });

    const data = await res.json();

    if (res.ok) {
        window.location.href = "/index";
    } else {
        alert(data.error);
    }
});

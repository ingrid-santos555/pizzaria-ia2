const chatBody = document.querySelector(".chat-body");
const messageInput = document.querySelector(".message-input");
const sendMessageButton = document.querySelector("#send-message");
const chatForm = document.querySelector(".chat-form");

let isSending = false; // 🔹 evita envio duplo

const userData = { message: null };


// 🔹 Cria elemento de mensagem
const createMessageElement = (content, ...classes) => {
    const div = document.createElement("div");
    div.classList.add("message", ...classes);
    div.innerHTML = content;
    return div;
};


// 🔹 Envia mensagem do usuário
const handleOutgoingMessage = async (event) => {

    if (event) event.preventDefault();

    if (isSending) return;

    userData.message = messageInput.value.trim();

    if (!userData.message) return;

    isSending = true;

    messageInput.value = "";


    // 🔹 Balão do usuário
    const outgoingMessageDiv = createMessageElement(
        `<div class="message-text">${userData.message}</div>`,
        "user-message"
    );

    chatBody.appendChild(outgoingMessageDiv);
    chatBody.scrollTop = chatBody.scrollHeight;


    // 🔹 Balão do bot (thinking)
    const incomingMessageDiv = createMessageElement(
        `
        <svg class="bot-avatar" xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 1024 1024">
            <path d="M738.3 287.6H285.7c-59 0-106.8 47.8-106.8 106.8v303.1c0 59 47.8 106.8 106.8 106.8h81.5v111.1c0 .7.8 1.1 1.4.7l166.9-110.6 41.8-.8h117.4l43.6-.4c59 0 106.8-47.8 106.8-106.8V394.5c0-59-47.8-106.9-106.8-106.9z"/>
        </svg>
        <div class="message-text">
            <div class="thinking-indicator">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        </div>
        `,
        "bot-message",
        "thinking"
    );

    chatBody.appendChild(incomingMessageDiv);
    chatBody.scrollTop = chatBody.scrollHeight;


    try {

        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: userData.message
            })
        });

        if (!response.ok) {
            throw new Error("Erro na resposta do servidor");
        }

        const data = await response.json();

        incomingMessageDiv.classList.remove("thinking");

        const botReply = data.reply || "Erro inesperado na resposta.";

        // 🔹 mantém robô e permite quebra de linha
        const formatarResposta = (texto) => {
        return texto
        .replace(/\n/g, "<br>")
        .replace(/(\/acompanhar\/[^\s<]+)/g, '<a href="$1" target="_blank" style="color:#ff5c28;text-decoration:underline;">Acompanhar pedido</a>');
};

incomingMessageDiv.querySelector(".message-text").innerHTML = formatarResposta(botReply);
        chatBody.scrollTop = chatBody.scrollHeight;

    } catch (error) {

        incomingMessageDiv.classList.remove("thinking");

        incomingMessageDiv.querySelector(".message-text").innerHTML =
            "Erro ao conectar com o servidor.";

    }

    isSending = false;
};


// 🔹 Previne reload do form
chatForm.addEventListener("submit", handleOutgoingMessage);


// 🔹 Enter envia mensagem (Shift+Enter quebra linha)
messageInput.addEventListener("keydown", (e) => {

    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleOutgoingMessage();
    }

});


// 🔹 Clique no botão envia mensagem
sendMessageButton.addEventListener("click", handleOutgoingMessage);
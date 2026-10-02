async function enviarMensajeIA() {
    const input = document.getElementById('chatInput');
    const mensaje = input.value.trim();
    const clienteSelect = document.getElementById('chatClienteSelect');
    const clienteId = clienteSelect ? clienteSelect.value : null;

    if (!mensaje) return;

    const messagesContainer = document.getElementById('chatMessages');

    // Burbuja de usuario
    const userBubble = document.createElement('div');
    userBubble.className = 'chat-bubble user';
    userBubble.textContent = mensaje;
    messagesContainer.appendChild(userBubble);

    input.value = '';
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // Burbuja de carga
    const loadingBubble = document.createElement('div');
    loadingBubble.className = 'chat-bubble assistant';
    loadingBubble.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.5rem; color: var(--text-muted);">
            <i data-lucide="loader-2" class="spin" style="width: 16px; height: 16px;"></i>
            <span>Consultando expediente y procesando con Groq (openai/gpt-oss-20b)...</span>
        </div>
    `;
    messagesContainer.appendChild(loadingBubble);
    if (window.lucide) lucide.createIcons();
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    try {
        const response = await fetch('/ia/consultar/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                pregunta: mensaje,
                cliente_id: clienteId
            })
        });

        const data = await response.json();
        if (data.respuesta) {
            // Formateo Markdown a HTML enriquecido
            let formatted = data.respuesta
                .replace(/^### (.*$)/gim, '<h4 style="font-weight: 700; margin-top: 0.75rem; margin-bottom: 0.35rem; color: var(--text-primary);">$1</h4>')
                .replace(/^## (.*$)/gim, '<h3 style="font-weight: 800; margin-top: 0.9rem; margin-bottom: 0.4rem; color: var(--text-primary);">$1</h3>')
                .replace(/^# (.*$)/gim, '<h2 style="font-weight: 800; margin-top: 1rem; margin-bottom: 0.5rem; color: var(--text-primary);">$1</h2>')
                .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/gim, '<em>$1</em>')
                .replace(/^\* (.*$)/gim, '<li style="margin-left: 1.25rem;">$1</li>')
                .replace(/^- (.*$)/gim, '<li style="margin-left: 1.25rem;">$1</li>')
                .replace(/\n/gim, '<br>');

            loadingBubble.innerHTML = `
                <div style="line-height: 1.6; color: var(--text-primary); font-size: 0.9rem;">
                    ${formatted}
                </div>
            `;
        } else if (data.error) {
            loadingBubble.innerHTML = `<span style="color: var(--danger); font-weight: 600;">Error: ${data.error}</span>`;
        } else {
            loadingBubble.innerHTML = '<span style="color: var(--danger);">Ocurrió un error al procesar la respuesta.</span>';
        }
    } catch (e) {
        loadingBubble.innerHTML = `<span style="color: var(--danger);">Error de conexión con el servidor: ${e.message}</span>`;
    }

    if (window.lucide) lucide.createIcons();
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('chatInput');
    if (input) {
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                enviarMensajeIA();
            }
        });
    }
});

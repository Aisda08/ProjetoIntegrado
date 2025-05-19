const BASE_URL = `http://${window.location.hostname}:5000`;

function url(path) {
    return `${BASE_URL}${path}`;
}

async function fetchJson(url, options = {}) {
    try {
        const res = await fetch(url, options);
        if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || "Erro na requisição");
        }
        return await res.json();
    } catch (error) {
        console.error(error);
        throw error;
    }
}

function formatarCelular(celular) {
    return `(${celular.slice(0, 2)}) ${celular.slice(2, 7)}-${celular.slice(7)}`;
}

function formatarCPF(cpf) {
    return `${cpf.slice(0, 3)}.${cpf.slice(3, 6)}.${cpf.slice(6, 9)}-${cpf.slice(9, 11)}`;
}

function obterParametroCPF() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get("cpf");
}

async function carregarDadosUsuario() {
    const cpf = obterParametroCPF();
    if (!cpf) return alert("CPF não informado na URL.");

    try {
        const usuario = await fetchJson(url(`/api/usuario?cpf=${cpf}`));

        document.getElementById("nome").value = usuario.nome;
        document.getElementById("cpf").value = formatarCPF(usuario.cpf);
        
        document.getElementById("photo-preview").src = usuario.foto_path;

        document.getElementById("email").value = usuario.email;
        document.getElementById("celular").value = formatarCelular(usuario.celular);

    } catch (erro) {
        alert("Erro ao carregar os dados do usuário.");
    }
}

function cancelarEdicao() {
    window.location.href = url("/gerenciar_usuarios");
}

async function deletarUsuario() {
    const cpf = obterParametroCPF();
    if (!confirm("Tem certeza que deseja deletar este usuário?")) return;

    try {
        await fetchJson(url(`/api/usuarios/${cpf}`), { method: "DELETE" });
        alert("Usuário deletado com sucesso.");
        window.location.href = url("/gerenciar_usuarios");
    } catch (erro) {
        alert("Erro ao deletar usuário: " + erro.message);
    }
}

function validaFoto() {
    return typeof imagemBase64 === 'string' && imagemBase64.startsWith('data:image/');
}

function validarEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

function validarCelular(numero) {
    const limpo = numero.replace(/\D/g, '');
    return /^(\d{2})9\d{8}$/.test(limpo);
}

async function abrirCamera() {
    document.getElementById("capture-camera-button").style.display = "none";
    document.getElementById("camera").style.display = "none";
    document.getElementById("camera-container").style.display = "flex";
    document.getElementById("loading-camera").style.display = "flex";
    document.getElementById("add-photo-container").style.display = "none";

    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        const video = document.getElementById("video");
        video.srcObject = stream;
    } catch (err) {
        alert("Erro ao acessar a webcam: " + err.message);
    } finally {
        document.getElementById("loading-camera").style.display = "none";
        document.getElementById("camera").style.display = "flex";
        document.getElementById("capture-camera-button").style.display = "block";
    }
}

function capturarFoto() {
    const video = document.getElementById("video");
    const canvas = document.getElementById("canvas");
    const context = canvas.getContext("2d");
    
    // Espelhar imagem no canvas para manter o efeito de espelho na captura
    context.translate(canvas.width, 0);
    context.scale(-1, 1);
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    context.setTransform(1, 0, 0, 1, 0, 0); // Resetar transformações

    imagemBase64 = canvas.toDataURL("image/png");
    document.getElementById("photo-preview").src = imagemBase64;

    // Para a câmera após capturar
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }

    document.getElementById("camera-container").style.display = "none";
    document.getElementById("main-inputs-container-svg").style.display = "none";
    document.getElementById("photo-preview").style.display = "block";
    document.getElementById("add-photo-container").style.display = "block";
}

async function atualizarUsuario() {
    const cpf = obterParametroCPF();
    const nome = document.getElementById("nome").value.trim();
    const email = document.getElementById("email").value.trim();
    const celular = document.getElementById("celular").value.replace(/\D/g, "");
    const foto_base64 = imagemBase64;

    // Validar dados em branco.
    if (!cpf || !nome || !email || !celular) {
        return alert("Preencha todos os campos obrigatórios.");
    }

    if (!validaFoto()) return alert("Foto inválida.")

    if (!validarEmail(email)) return alert("Email inválido.");

    if (!validarCelular(celular)) return alert("Número de celular inválido.");

    const dadosAtualizados = { cpf, nome, email, celular, foto_base64};

    try {
        await fetchJson(url(`/api/usuarios/${cpf}`), {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dadosAtualizados),
        });
        alert("Usuário atualizado com sucesso.");
        window.location.href = url("/gerenciar_usuarios");
    } catch (erro) {
        alert("Erro ao atualizar o usuário: " + erro.message);
    }
}

window.onload = carregarDadosUsuario;
let imagemBase64 = "";
let stream = null;

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

function validarCPF(cpf) {
    const limpo = cpf.replace(/\D/g, '');
    return /^\d{11}$/.test(limpo);
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


async function enviar() {
    const nome = document.getElementById("nome").value.trim();
    const cpf = document.getElementById("cpf").value.trim();
    const email = document.getElementById("email").value.trim();
    const celular = document.getElementById("celular").value.trim();

    if (!nome || !cpf || !email || !celular || !imagemBase64) {
        return alert("Preencha todos os campos obrigatórios.");
    }

    if (!validarCPF(cpf)) return alert("CPF inválido.")

    if (!validaFoto()) return alert("Foto inválida.")

    if (!validarEmail(email)) return alert("Email inválido.");

    if (!validarCelular(celular)) return alert("Número de celular inválido.");

    try {
        const resposta = await fetch('http://localhost:5000/inserirUsuario', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nome, cpf, email, celular, foto_base64: imagemBase64 })
        });

        alert("Usuário inserido com sucesso!");
        location.reload();
    } catch (error) {
        alert("Erro ao enviar dados: " + error.message);
    }
}
let imagemBase64 = "";
let stream = null;

async function abrirCamera() {
    document.getElementById("camera-container").style.display = "flex";
    document.getElementById("photo-container").style.display = "none";

    // Solicita acesso à webcam somente quando o botão for clicado
    try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true });
    const video = document.getElementById("video");
    video.srcObject = stream;
    } catch (err) {
    alert("Erro ao acessar a webcam: " + err.message);
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
    document.getElementById("fotoPreview").src = imagemBase64;

    // Para a câmera após capturar
    if (stream) {
    stream.getTracks().forEach(track => track.stop());
    }

    document.getElementById("camera-container").style.display = "none";
    document.getElementById("add-photo-button").style.display = "block";
}

async function enviar() {
    const nome = document.getElementById("nome").value;
    const cpf = document.getElementById("cpf").value;

    const resposta = await fetch('http://localhost:5000/inserir', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ nome, cpf, foto: imagemBase64 })
    });

    const texto = await resposta.text();
    alert(texto);
}
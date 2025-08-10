function formatarCPF(cpf) {
    return `${cpf.slice(0, 3)}.${cpf.slice(3, 6)}.${cpf.slice(6, 9)}-${cpf.slice(9, 11)}`;
}

function formatarCelular(celular) {
    return `(${celular.slice(0, 2)}) ${celular.slice(2, 7)}-${celular.slice(7)}`;
}

async function carregarUsuarios() {
    try {
        const resposta = await fetch(`http://127.0.0.1:${window.location.port}/api/usuarios`);
        const usuarios = await resposta.json();
        const corpoTabela = document.querySelector("#tabelaUsuarios tbody");

        if (usuarios.length === 0) {
            const linha = document.createElement("tr");
            const celula = document.createElement("td");
            celula.colSpan = 4;
            celula.style.textAlign = "center";
            celula.textContent = "Nenhum Usuário Cadastrado!";
            linha.appendChild(celula);
            corpoTabela.appendChild(linha);
            return;
        }

        usuarios.forEach(usuario => {
            const linha = document.createElement("tr");

            linha.innerHTML = `
                <td>${usuario.nome}</td>
                <td>${formatarCPF(usuario.cpf)}</td>
                <td>${usuario.email}</td>
                <td>${formatarCelular(usuario.celular)}</td>
            `;

            linha.addEventListener("click", () => {
                window.location.href = `editar_usuario?cpf=${usuario.cpf}`;
            });

            corpoTabela.appendChild(linha);
        });
    } catch (erro) {
        console.error("Erro ao carregar usuários:", erro);
    }
}


window.onload = carregarUsuarios;
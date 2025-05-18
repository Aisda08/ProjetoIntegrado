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

async function atualizarUsuario() {
  const cpf = obterParametroCPF();
  const nome = document.getElementById("nome").value;
  const email = document.getElementById("email").value;
  const celular = document.getElementById("celular").value.replace(/\D/g, "");

  if (!cpf || !nome || !email || !celular) {
    alert("Preencha todos os campos obrigatórios.");
    return;
  }

  const dadosAtualizados = { cpf, nome, email, celular };

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
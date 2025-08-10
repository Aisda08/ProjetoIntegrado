function validarLogin() {
    const user = document.getElementById('user').value;
    const password = document.getElementById('password').value;

    if (user === 'admin' && password === 'senha') {
        sessionStorage.setItem('autenticado', 'true');

        document.querySelector('.login-container').style.display = 'none';
        document.querySelector('.home-container').style.display = 'block';
        document.title = "Página Inicial";
    } else {
        alert('Usuário ou senha incorretos!');
    }
}

window.addEventListener('load', function() {
    if (sessionStorage.getItem('autenticado') === 'true') {
        document.querySelector('.login-container').style.display = 'none';
        document.querySelector('.home-container').style.display = 'block';
        document.title = "Página Inicial";
    }
});
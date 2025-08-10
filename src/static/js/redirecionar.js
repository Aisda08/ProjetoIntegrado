const host = window.location.hostname;
const port = window.location.port;
function redirecionar(pag) {
    window.location.href = `http://${host}:${port}/${pag}`;
}

window.addEventListener('load', function() {
    if (!sessionStorage.getItem('autenticado') && window.location.pathname != "/") {
        redirecionar("")
    }
});
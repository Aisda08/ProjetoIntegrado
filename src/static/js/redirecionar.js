const host = window.location.hostname;
const port = window.location.port;
function redirecionar(pag) {
    window.location.href = `http://${host}:${port}/${pag}`;
}
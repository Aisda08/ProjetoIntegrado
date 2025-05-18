const host = window.location.hostname;
const port = 5000;
function redirecionar(pag) {
    window.location.href = `http://${host}:${port}/${pag}`;
}
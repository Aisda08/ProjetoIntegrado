fetch("static/html/header.html")
    .then(res => res.text())
    .then(data => {
        const headerElement = document.createElement("header");
        headerElement.innerHTML = data;
        document.body.prepend(headerElement);
    });

fetch("static/html/footer.html")
    .then(res => res.text())
    .then(data => {
        const footerElement = document.createElement("footer");
        footerElement.innerHTML = data;
        document.body.append(footerElement);
    });
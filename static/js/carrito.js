// static/js/carrito.js

document.addEventListener("DOMContentLoaded", () => {
    // Actualizar cantidad en el carrito
    const cantidadInputs = document.querySelectorAll(".form-cantidad input");

    cantidadInputs.forEach(input => {
        input.addEventListener("change", (e) => {
            if (parseInt(e.target.value) < 1) {
                e.target.value = 1;
            }
        });
    });

    // Confirmación al vaciar carrito
    const vaciarBtn = document.querySelector(".btn-secundario");
    if (vaciarBtn) {
        vaciarBtn.addEventListener("click", (e) => {
            if (!confirm("¿Seguro que querés vaciar el carrito?")) {
                e.preventDefault();
            }
        });
    }
});

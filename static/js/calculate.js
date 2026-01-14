document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll('[data-type="copy"]').forEach(button => {
        button.addEventListener("click", () => {
            const row = button.closest("tr");
            const valueCell = row.querySelector('[data-type="copy_value"]');
            const text = valueCell?.innerText || "";

            navigator.clipboard.writeText(text)
                .then(() => console.log("Copiado:", text))
                .catch(err => console.error("Error al copiar:", err));
        });
    });
});

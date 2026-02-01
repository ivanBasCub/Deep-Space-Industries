document.addEventListener("DOMContentLoaded", () =>{
    const input = document.getElementById("inputSearch")
    const tbody = document.querySelector("#userTable tbody")

    input.addEventListener("input", () => {
        const filter = input.value.toLowerCase().trim();
        const rows = tbody.querySelectorAll("tr");

        rows.forEach(row => {
            const name = row.querySelector("td:first-child").innerText.toLowerCase();
            row.style.display = name.includes(filter) ? "" : "none";
        })
    })
})
document.addEventListener("DOMContentLoaded", () => {

    const inputName = document.getElementById("filterItemName");
    const selectTag = document.getElementById("filtertag");
    const selectLocation = document.getElementById("filterlocation");
    const selectStation = document.getElementById("filterstation");

    const rows = document.querySelectorAll("tbody tr");

    function filterTable() {
        const nameValue = inputName.value.toLowerCase();
        const tagValue = selectTag.value.toLowerCase();
        const locationValue = selectLocation.value.toLowerCase();
        const stationValue = selectStation.value.toLowerCase();

        rows.forEach(row => {
            const name = row.children[2].textContent.toLowerCase();
            const tags = row.children[4].textContent.toLowerCase();
            const location = row.children[5].textContent.toLowerCase();
            const station = row.children[6].textContent.toLowerCase();

            let visible = true;

            // Filtro por nombre
            if (nameValue && !name.includes(nameValue)) {
                visible = false;
            }

            // Filtro por tag
            if (tagValue && !tags.includes(tagValue)) {
                visible = false;
            }

            // Filtro por location
            if (locationValue && location !== locationValue) {
                visible = false;
            }

            // Filtro por station
            if (stationValue && station !== stationValue) {
                visible = false;
            }

            row.style.display = visible ? "" : "none";
        });
    }

    // Eventos
    inputName.addEventListener("input", filterTable);
    selectTag.addEventListener("change", filterTable);
    selectLocation.addEventListener("change", filterTable);
    selectStation.addEventListener("change", filterTable);
});



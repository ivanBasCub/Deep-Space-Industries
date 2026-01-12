document.addEventListener("DOMContentLoaded", () => {
    const select = document.getElementById("program_services");
    const freight_tax = document.getElementById("tax");

    select.addEventListener("change", () => {
        const select_services = Array.from(select.selectedOptions).map(opt => opt.value);

        if (select_services.includes("2")){
            freight_tax.style.display="block";
        }else{
            freight_tax.style.display="none";
        }
    })
})
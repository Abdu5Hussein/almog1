document.addEventListener('DOMContentLoaded', function () {

    // Handle row click to pre-fill the form for editing
    document.querySelectorAll("table tbody tr").forEach((row) => {
        row.addEventListener("click", () => {
            document.getElementById("countryId").value = row.cells[0].innerText;
            document.getElementById("inputName").value = row.cells[1].innerText;
        });
    });

    // Form validation
    (function () {
        "use strict";

        const forms = document.querySelectorAll(".needs-validation");

        Array.from(forms).forEach((form) => {
            form.addEventListener(
                "submit",
                (event) => {
                    if (!form.checkValidity()) {
                        event.preventDefault();
                        event.stopPropagation();
                    }
                    form.classList.add("was-validated");
                },
                false
            );
        });
    })();
});
document.addEventListener("DOMContentLoaded", function () {
    // JavaScript to filter the table based on selected MainType
    document
        .getElementById("item-main-filter")
        .addEventListener("change", function () {
            const selectedValue = this.value;
            const rows = document.querySelectorAll("#models-table tbody tr");

            rows.forEach(function (row) {
                const mainTypeId = row.getAttribute("data-sub-type");

                if (selectedValue === "" || selectedValue === mainTypeId) {
                    row.style.display = ""; // Show row if it matches
                } else {
                    row.style.display = "none"; // Hide row if it doesn't match
                }
            });
        });
    // Form validation
    (function () {
        "use strict";
        const forms = document.querySelectorAll(".needs-validation");
        Array.from(forms).forEach((form) => {
            form.addEventListener(
                "submit",
                function (event) {
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

    //////
    document.querySelectorAll("tr").forEach((row) => {
        row.addEventListener("click", function () {
            const id = this.children[0].innerText; // Assuming the first column is the ID
            const name = this.children[1].innerText; // Assuming the second column is the name

            document.getElementById("modelId").value = id;
            document.getElementById("model-name").value = name;
        });
    });

    // Select the form elements and buttons
    const itemMainFilter = document.getElementById("item-main-filter");
    const addButton = document.getElementById("add-button");
    const editButton = document.getElementById("edit-button");
    const deleteButton = document.getElementById("delete-button");

    // Set up event listeners for the buttons
    addButton.addEventListener("click", function () {
        // Make the item-main-filter required when adding
        itemMainFilter.setAttribute("required", "true");
    });

    editButton.addEventListener("click", function () {
        // Remove the required attribute for editing
        itemMainFilter.removeAttribute("required");
    });

    deleteButton.addEventListener("click", function () {
        // Remove the required attribute for deleting
        itemMainFilter.removeAttribute("required");
    });
});
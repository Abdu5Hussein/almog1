document.addEventListener("DOMContentLoaded", function () {
    function getCSRFToken() {
        const csrfInput = document.querySelector("[name=csrfmiddlewaretoken]");
        return csrfInput ? csrfInput.value : "";
    }

    function updateValues(action, value, field) {
        function getItemIdFromUrl() {
            const urlPath = window.location.pathname; // Get the full path
            const segments = urlPath.split('/'); // Split by '/' to get segments
            const itemId = segments[segments.length - 2]; // Assuming itemId is the second last segment
            return itemId;
        }

        // Usage
        const itemId = getItemIdFromUrl();
        if (!itemId) {
            alert("no item id was provided");
            return
        }
        const body = {
            'action': action,
            'value': value
        };

        customFetch(`http://45.13.59.226/item/${itemId}/update-${field}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify(body),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`Error ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then((data) => {
                alert("! تم تحديث البيان !"); // Assuming your API returns a message
                location.reload();
                // Optionally, you can also update the UI here with the new values
            })
            .catch((error) => {
                console.error("Error updating main item:", error.message);
                alert("An error occurred: " + error.message); // Show user-friendly error
            });
    }

    document.getElementById('btn-main-add').addEventListener('click', function () {
        const value = document.getElementById('maintype').value;
        updateValues('add', value, 'main');
    });
    document.getElementById('btn-main-remove').addEventListener('click', function () {
        const value = document.getElementById('maintype').value;
        updateValues('remove', value, 'main');
    });


    document.getElementById('btn-sub-add').addEventListener('click', function () {
        const value = document.getElementById('subtype').value;
        updateValues('add', value, 'sub');
    });
    document.getElementById('btn-sub-remove').addEventListener('click', function () {
        const value = document.getElementById('subtype').value;
        updateValues('remove', value, 'sub');
    });


    document.getElementById('btn-model-add').addEventListener('click', function () {
        const value = document.getElementById('model').value;
        updateValues('add', value, 'model');
    });
    document.getElementById('btn-model-remove').addEventListener('click', function () {
        const value = document.getElementById('model').value;
        updateValues('remove', value, 'model');
    });

    document.getElementById('btn-engine-add').addEventListener('click', function () {
        const value = document.getElementById('engine').value;
        updateValues('add', value, 'engine');
    });
    document.getElementById('btn-engine-remove').addEventListener('click', function () {
        const value = document.getElementById('engine').value;
        updateValues('remove', value, 'engine');
    });

    // Select table and dropdown
    const engines_table = document.getElementById("engines-table");
    const engine_select = document.getElementById("engine");

    const models_table = document.getElementById("models-table");
    const model_select = document.getElementById("model");

    const main_table = document.getElementById("main-table");
    const main_select = document.getElementById("maintype");

    const sub_table = document.getElementById("sub-table");
    const sub_select = document.getElementById("subtype");

    // Add event listener to the table
    engines_table.addEventListener("click", function (event) {
        // Check if a table cell (td) was clicked
        if (event.target && event.target.nodeName === "TD") {
            // Get the text content of the clicked cell
            const clickedValue = event.target.textContent.trim();

            // Check if the value exists in the select options
            let optionExists = false;
            for (let option of engine_select.options) {
                if (option.value === clickedValue) {
                    optionExists = true;
                    break;
                }
            }

            // If the value doesn't exist, add it to the options
            if (!optionExists) {
                const newOption = document.createElement("option");
                newOption.value = clickedValue;
                newOption.textContent = clickedValue;
                engine_select.appendChild(newOption);
            }

            // Set the select value to the clicked cell value
            engine_select.value = clickedValue;
        }
    });

    models_table.addEventListener("click", function (event) {
        // Check if a table cell (td) was clicked
        if (event.target && event.target.nodeName === "TD") {
            // Get the text content of the clicked cell
            const clickedValue = event.target.textContent.trim();

            // Check if the value exists in the select options
            let optionExists = false;
            for (let option of engine_select.options) {
                if (option.value === clickedValue) {
                    optionExists = true;
                    break;
                }
            }

            // If the value doesn't exist, add it to the options
            if (!optionExists) {
                const newOption = document.createElement("option");
                newOption.value = clickedValue;
                newOption.textContent = clickedValue;
                engine_select.appendChild(newOption);
            }

            // Set the select value to the clicked cell value
            model_select.value = clickedValue;
        }
    });

    sub_table.addEventListener("click", function (event) {
        // Check if a table cell (td) was clicked
        if (event.target && event.target.nodeName === "TD") {
            // Get the text content of the clicked cell
            const clickedValue = event.target.textContent.trim();

            // Check if the value exists in the select options
            let optionExists = false;
            for (let option of engine_select.options) {
                if (option.value === clickedValue) {
                    optionExists = true;
                    break;
                }
            }

            // If the value doesn't exist, add it to the options
            if (!optionExists) {
                const newOption = document.createElement("option");
                newOption.value = clickedValue;
                newOption.textContent = clickedValue;
                engine_select.appendChild(newOption);
            }

            // Set the select value to the clicked cell value
            sub_select.value = clickedValue;
        }
    });

    main_table.addEventListener("click", function (event) {
        // Check if a table cell (td) was clicked
        if (event.target && event.target.nodeName === "TD") {
            // Get the text content of the clicked cell
            const clickedValue = event.target.textContent.trim();

            // Check if the value exists in the select options
            let optionExists = false;
            for (let option of engine_select.options) {
                if (option.value === clickedValue) {
                    optionExists = true;
                    break;
                }
            }

            // If the value doesn't exist, add it to the options
            if (!optionExists) {
                const newOption = document.createElement("option");
                newOption.value = clickedValue;
                newOption.textContent = clickedValue;
                engine_select.appendChild(newOption);
            }

            // Set the select value to the clicked cell value
            main_select.value = clickedValue;
        }
    });
});

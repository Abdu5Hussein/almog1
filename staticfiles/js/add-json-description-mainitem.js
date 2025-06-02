document.addEventListener("DOMContentLoaded", function () {
    function addKeyValue() {
        // Create a new key-value pair div with inputs for key and value
        const container = document.getElementById("keyValueContainer");
        const newPair = document.createElement("div");
        newPair.classList.add("key-value-pair", "d-flex", "mb-3");

        newPair.innerHTML = `
            <input type="text" name="key" class="form-control me-2" placeholder="Key" required>
            <input type="text" name="value" class="form-control me-2" placeholder="Value" required>
            <button type="button" class="remove-btn btn" onclick="removeKeyValue(this)">Remove</button>
        `;

        container.appendChild(newPair);
    }

    function removeKeyValue(button) {
        // Remove the parent div of the clicked remove button
        button.parentElement.remove();
    }
    document.getElementById("addKey").addEventListener("click", addKeyValue);
    document.getElementById("removeKey").addEventListener("click", removeKeyValue);

    document.getElementById("pno").addEventListener("change", function () {
        // Get the selected option element
        const selectedOption = this.options[this.selectedIndex];

        // Retrieve the data-name and data-company attributes
        const name = selectedOption.getAttribute("data-name");
        const company = selectedOption.getAttribute("data-company");

        // Set the values into the input fields
        document.getElementById("name").value = name;
        document.getElementById("company").value = company;
    });
    document.getElementById("keyValueForm").addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent default form submission

        // Create an object to hold the key-value pairs
        const keyValuePairs = {};

        // Get all key-value pair inputs
        document.querySelectorAll(".key-value-pair").forEach(function (pair) {
            const key = pair.querySelector("input[name='key']").value.trim();
            const value = pair.querySelector("input[name='value']").value.trim();
            if (key) {
                keyValuePairs[key] = value;
            }
        });

        // Get the selected product ID (pno)
        const pno = document.getElementById("pno").value;

        if (!pno) {
            alert("Please select a product.");
            return;
        }

        // Convert key-value pairs to JSON
        const jsonData = {
            json: keyValuePairs
        };

        // Send the POST request to Django API
        fetch(`/api/products/${pno}/add-json-description`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify(jsonData)
        })
            .then(response => response.json())
            .then(data => {
                console.log("Success:", data);
                alert("JSON description added successfully!");
            })
            .catch(error => {
                console.error("Error:", error);
                alert("Failed to add JSON description.");
            });
    });
});
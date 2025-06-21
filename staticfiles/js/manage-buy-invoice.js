document.addEventListener('DOMContentLoaded', function () {

    const contextData = {
        id: "{{ auto_id|escapejs }}",
        currency: "{{ currency|escapejs }}",
        rate: parseFloat("{{ rate|escapejs }}"), // Ensure `rate` is a number
    };
    console.log(contextData);
    document
        .getElementById("new-org")
        .addEventListener("change", function () {
            const org_value = document.getElementById("new-org").value;
            const rate = contextData["rate"];
            document.getElementById("new-order").value =
                parseFloat(org_value) * parseFloat(rate);

            console.log(org_value);
            console.log(rate);
        });

    document
        .getElementById("edit-button")
        .addEventListener("click", function () {
            // Get new values from the input fields
            const newOrg = document.getElementById("new-org").value;
            const newOrder = document.getElementById("new-order").value;
            const newQuantity = document.getElementById("new-quantity").value;
            const invoice_no = document.getElementById("receipt-no").value;

            const id = contextData["id"]; // Retrieve the client ID from the URL (e.g., ?id=123)

            // Validate inputs (you can add more checks here)
            if (!newOrg || !newOrder || !newQuantity) {
                alert("Please fill in all fields.");
                return;
            }

            // Create data object to send to the server
            const data = {
                org: newOrg,
                order: newOrder,
                quantity: newQuantity,
                invoice_no: invoice_no,
                id: id,
            };

            // Send the data to the server using fetch (AJAX)
            customFetch("/update-buyinvoiceitem", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(data),
            })
                .then((response) => response.json())
                .then((data) => {
                    // Handle success or failure response from the server
                    if (data.success) {
                        alert("Item updated successfully!");
                        // Optionally, update the UI or redirect the user
                    } else {
                        alert("Failed to update item.");
                    }
                })
                .catch((error) => {
                    console.error("Error:", error);
                    alert("An error occurred.");
                });
        });

    document
        .getElementById("delete-button")
        .addEventListener("click", function () {
            const id = document.getElementById("auto_id").value; // Retrieve the client ID from the URL (e.g., ?id=123)
            console.log(id);
            if (!id) {
                alert("Please select an item to delete");
            }

            // Create data object to send to the server
            const data = {
                id: id,
            };

            if (!confirm("هل تريد حذف هذا الصنف ؟")) {
                return;
            }

            // Send the data to the server using fetch (AJAX)
            customFetch("/delete-buyinvoiceitem", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(data),
            })
                .then((response) => response.json())
                .then((data) => {
                    // Handle success or failure response from the server
                    if (data.success) {
                        alert("تم حذف الصنف بنجاح, سيتم اغلاق هذه النافذة!");
                        window.close();
                        // Optionally, update the UI or redirect the user
                    } else {
                        alert("Failed to delete item.");
                    }
                })
                .catch((error) => {
                    console.error("Error:", error);
                    alert("An error occurred.");
                });
        });
});
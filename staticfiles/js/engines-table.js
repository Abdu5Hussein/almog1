document.addEventListener('DOMContentLoaded', function () {
    function addEngine() {
        const data = {
            "engine_name": document.getElementById("engine-name").value,
            "maintype_str": Array.from(document.getElementById("item-main").selectedOptions)
                .map(option => option.value)
                .join(';'),
            "subtype_str": Array.from(document.getElementById("item-sub").selectedOptions)
                .map(option => option.value)
                .join(';'),
        }
        console.log(data);

        customFetch('/engines/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),  // Stringify the data here
        })
            .then(response => {
                if (response.ok || response.status === 201) {
                    return response.json(); // If successful or created, parse the response
                } else {
                    throw new Error('Failed to create engine'); // Throw an error for any other status
                }
            })
            .then(data => {
                console.log(data);
                alert('تمت العملية بنجاح!'); // Show success message if the operation is successful
            })
            .catch(error => {
                alert('حدث خطأ، حاول مرة أخرى.'); // Show error message if something goes wrong
            }).finally(() => {
                location.reload();
            });
    }

    function editEngine() {
        const data = {
            "engine_name": document.getElementById("engine-name").value,
            "maintype_str": Array.from(document.getElementById("item-main").selectedOptions)
                .map(option => option.value)
                .join(';'),
            "subtype_str": Array.from(document.getElementById("item-sub").selectedOptions)
                .map(option => option.value)
                .join(';'),
        }
        console.log(data);

        customFetch('/engines/', {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),  // Stringify the data here
        })
            .then(response => {
                if (response.ok || response.status === 201) {
                    return response.json(); // If successful or created, parse the response
                } else {
                    throw new Error('Failed to update engine'); // Throw an error for any other status
                }
            })
            .then(data => {
                console.log(data);
                alert('تم التعديل بنجاح!'); // Show success message if the operation is successful
            })
            .catch(error => {
                alert('حدث خطأ، حاول مرة أخرى.'); // Show error message if something goes wrong
            }).finally(() => {
                location.reload();
            });
    }

    function editEngine() {
        const data = {
            "engine_name": document.getElementById("engine-name").value,
            "maintype_str": Array.from(document.getElementById("item-main").selectedOptions)
                .map(option => option.value)
                .join(';'),
            "subtype_str": Array.from(document.getElementById("item-sub").selectedOptions)
                .map(option => option.value)
                .join(';'),
        }
        console.log(data);
        const id = document.getElementById("engineId").value;
        customFetch(`/engines/${id}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),  // Stringify the data here
        })
            .then(response => {
                if (response.ok || response.status === 201) {
                    return response.json(); // If successful or created, parse the response
                } else {
                    throw new Error('Failed to update engine'); // Throw an error for any other status
                }
            })
            .then(data => {
                console.log(data);
                alert('تم التعديل بنجاح!'); // Show success message if the operation is successful
            })
            .catch(error => {
                alert('حدث خطأ، حاول مرة أخرى.'); // Show error message if something goes wrong
            }).finally(() => {
                location.reload();
            });
    }

    function deleteEngine() {
        const idInput = document.getElementById("engineId");
        const id = idInput.value;
        const name = idInput.getAttribute("data-name");

        const result = confirm("هل أنت متأكد أنك تريد حذف هذا العنصر؟" + "  " + name);

        if (!result) {
            return
        }

        customFetch(`/engines/${id}/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            //body: JSON.stringify(data),  // Stringify the data here
        })
            .then(response => {
                if (response.status === 204) {
                    alert('تم الحذف بنجاح!'); // Show success message for status 204 (No Content)
                } else {
                    throw new Error('Failed to delete engine'); // Throw error for any other status
                }
            })
            .catch(error => {
                alert('حدث خطأ، حاول مرة أخرى.'); // Show error message if something goes wrong
            })
            .finally(() => {
                location.reload(); // Reload the page after the operation
            });
    }


    // Add event listener for rows
    document.querySelectorAll("tbody tr").forEach((row) => {
        row.addEventListener("click", function () {
            // Get the data-id from the clicked row
            const engineId = this.getAttribute("data-id");
            const engineName = this.cells[0].innerText;

            // Set the engineId input's value to the clicked row's id
            const engineIdInput = document.getElementById("engineId");
            const engineNameInput = document.getElementById("engine-name");
            engineIdInput.value = engineId;
            engineNameInput.value = engineName;

            // Add the data-id attribute to the engineId input
            engineIdInput.setAttribute("data-name", engineName);
            console.log("id:", engineIdInput.value);
            console.log("name:", engineName);
        });
    });

    document.getElementById("add-button").addEventListener('click', () => addEngine());
    document.getElementById("edit-button").addEventListener('click', () => editEngine());
    document.getElementById("delete-button").addEventListener('click', () => deleteEngine());
});
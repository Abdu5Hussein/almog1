document.addEventListener("DOMContentLoaded", function () {

    console.log(document.getElementById("invoice_no").selectedIndex);

    const table = new Tabulator("#users-table", {
        index: "fileid", // Use "fileid" as the unique row identifier
        height: "auto", // Adjust height or set a fixed height
        layout: "fitColumns",
        selectable: true,
        pagination: "local", // Enable local pagination
        paginationSize: 100, // Show 100 records per page
        paginationSizeSelector: [50, 100, 200], // Page size options
        paginationButtonCount: 5, // Number of visible pagination buttons
        movableColumns: true,
        columnHeaderVertAlign: "bottom",
        columnMenu: true, // Enable column menu
        data: [], // Placeholder, will be loaded dynamically
        columns: [
            { title: "الرقم الاصلي", field: "item_no", width: 90 },
            { title: "اسم الشركة", field: "company", width: 90 },
            { title: "رقم الشركة", field: "company_no", width: 90 },
            { title: "اسم الصنف", field: "name", width: 90 },
            { title: "سعر الشراء", field: "dinar_unit_price", width: 90 },
            { title: "اجمالي سعر الشراء", field: "dinar_total_price", width: 90 },
            { title: "الكمية", field: "quantity", width: 90 },
            { title: "ملاحظات", field: "note", width: 90 },
            { title: "cost_unit_price", field: "cost_unit_price", width: 90 },
            { title: "org_unit_price", field: "org_unit_price", width: 90 },
        ],
        placeholder: "No Data Available",
        rowFormatter: function (row) {
            var rowData = row.getData(); // Get the row data

            // You can add more conditions as needed
        }, // Message when no data is present or after filtering
        rowClick: function (e, row) {
            const clickedPno = row.getData().pno; // Get pno of the clicked row
            console.log("Clicked Pno:", clickedPno);
        },
        tableBuilt: function () {
            console.log("table built");
        },
    });
    document
        .getElementById("invoice_no")
        .addEventListener("change", function () {
            const selected = document.getElementById("invoice_no").selectedIndex;
            console.log(selected);
            if (selected != 0) {
                const invoice = document.getElementById("invoice_no").value;

                const data = {
                    invoice_no: invoice,
                };

                customFetch("/process_temp_confirm", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": "{{ csrf_token }}", // CSRF token for security
                    },
                    body: JSON.stringify(data), // Send the stringified data and invoice number
                })
                    .then((response) => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! Status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then((result) => {
                        console.log("Response from server:", result);
                        if (result.status === "success") {
                            //alert(result.message);

                            // Extract the invoice items from the result data
                            const invoiceItems = result.data.invoice_items;

                            // Assuming you have a Tabulator instance created and it's referenced by 'table'
                            table.setData(invoiceItems); // Populate the Tabulator table with invoice items

                            refresh_total();
                            document.getElementById("org-id").value =
                                result.data.original;
                            document.getElementById("date").value =
                                result.data.invoice_date;
                            document.getElementById("arrive-date").value =
                                result.data.arrive_date;
                            document.getElementById("source").value = result.data.source;
                        } else {
                            alert("Error: " + result.message);
                        }
                    })
                    .catch((error) => {
                        console.error("Error:", error);
                        alert("An error occurred while importing data.");
                    });
            } else {
                alert("الرجاء اختيار رقم الفاتورة");
            }
        });
    function calculateColumnSum(columnName) {
        let sum = 0;
        const rowData = table.getData(); // Fetch row data from Tabulator

        if (Array.isArray(rowData)) {
            // Ensure rowData is an array
            rowData.forEach((row) => {
                if (!isNaN(row[columnName])) {
                    sum += parseFloat(row[columnName]); // Convert to float and add to sum
                }
            });
        } else {
            console.error(
                `rowData is not an array or is undefined for column: ${columnName}`
            );
        }

        return parseFloat(sum);
    }
    refresh_total();
    function refresh_total() {
        const total = calculateColumnSum("dinar_total_price");
        document.getElementById("order-total").value = total;
    }

    document
        .getElementById("confirm-btn")
        .addEventListener("click", function () {
            const invoice = document.getElementById("invoice_no").value;
            // Assuming 'table' is your Tabulator instance
            const tabulatorData = table.getData(); // Get all rows' data from Tabulator

            const data = {
                invoice_no: invoice,
                table: tabulatorData,
            };
            console.log(data);

            if (invoice == "") {
                alert("الرجاء اختيار رقم الفاتورة");
                return;
            }
            customFetch("/confirm_temp_invoice", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": "{{ csrf_token }}", // CSRF token for security
                },
                body: JSON.stringify(data), // Send the stringified data and invoice number
            })
                .then((response) => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    return response.json();
                })
                .then((result) => {
                    console.log("Response from server:", result);
                    if (result.status === "success") {
                        alert(
                            ` تم ترحيل الفاتورة الخاصة بالرقم الالي ${invoice} بنجاح `
                        );
                    } else {
                        alert("Error: " + result.message);
                    }
                })
                .catch((error) => {
                    console.error("Error:", error);
                    alert("An error occurred while importing data.");
                });
        });
    document
        .getElementById("clear-btn")
        .addEventListener("click", function () {
            clearForm();
        });
    function clearForm() {
        window.requestAnimationFrame(function () {
            const formElements = document.querySelectorAll(
                " input,  select,  textarea"
            );
            formElements.forEach(function (element) {
                if (!element.classList.contains("value-fixed")) {
                    if (
                        element.tagName.toLowerCase() === "input" ||
                        element.tagName.toLowerCase() === "textarea"
                    ) {
                        element.value = ""; // Reset input and textarea values
                    } else if (element.tagName.toLowerCase() === "select") {
                        element.selectedIndex = 0; // Reset select dropdowns
                    }
                }
                document.getElementById("order-total").value = 0;
                console.log(document.getElementById("invoice_no").selectedIndex);

                table.replaceData([]);
            });
        });
    }

});
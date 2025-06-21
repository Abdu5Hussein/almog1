document.addEventListener('DOMContentLoaded', function () {
    const cost_table = new Tabulator("#cost-table", {
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
            { title: "رقم الي", field: "autoid", width: 90 },
            { title: "بيان التكلفة", field: "cost_for", width: 90 },
            { title: "القيمة بالعملة", field: "cost_price", width: 90 },
            { title: "سعر التحويل", field: "exchange_rate", width: 90 },
            { title: "القيمة بالليبي", field: "dinar_cost_price", width: 190 },
            { title: "الفاتورة", field: "invoice_no", width: 90, visible: false },
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
    const invoice = document.getElementById("invoice").value;

    if (invoice) {
        refreshCostsTable(invoice);
        refreshItemsTable(invoice);
    }

    cost_table.on("rowClick", function (e, row) {
        console.log("Row clicked after data update:", row.getData());
        const autoid = row.getData().autoid;
        alert("تم اختيار الصنف رقم : " + autoid + "يمكنك الان حذف او تعديل الصنف ");
        sessionStorage.setItem("session_autoid", autoid);
    });
    function removeCommas(value) {
        return parseFloat(value.replace(/,/g, ''));
    }
    function deleteRecord(autoid) {
        // Confirm before sending the delete request
        const confirmDelete = confirm("هل أنت متأكد أنك تريد حذف السجل رقم: " + autoid);

        if (confirmDelete) {
            // Send a DELETE request to the Django backend
            customFetch(`/delete-buyinvoice-cost/${autoid}/`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(), // Include CSRF token if using Django
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        alert("تم حذف السجل بنجاح.");
                        refreshCostsTable(invoice);
                    } else {
                        alert("فشل الحذف. الرجاء المحاولة لاحقًا.");
                    }
                })
                .catch(error => {
                    console.error('Error deleting record:', error);
                    alert("حدث خطأ أثناء الحذف.");
                });
        }
    }

    // Helper function to get the CSRF token from the document (if using Django)
    function getCsrfToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        return csrfToken;
    }

    const delete_btn = document.getElementById("delete_btn");
    delete_btn.addEventListener("click", function () {
        const id = sessionStorage.getItem("session_autoid");
        console.log("delete id", id);
        deleteRecord(id);
    })

    const edit_btn = document.getElementById("edit_btn");
    edit_btn.addEventListener("click", function () {
        const id = sessionStorage.getItem("session_autoid");
        console.log("edit_id", id);
    })

    function refreshItemsTable(invoice) {
        customFetch(`fetch-buy-invoice-items?id=${invoice}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
            .then((response) => response.json())
            .then((data) => {
                console.log("Fetched Data:", data);
                items_table.setData(data);
                refresh_teble_calc();
                calculateCostSum("cost_unit_price", "quantity");
            });
    }
    function refreshCostsTable(invoice) {
        customFetch(`fetch-costs?id=${invoice}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
            .then((response) => response.json())
            .then((data) => {
                console.log("Fetched Data:", data);
                cost_table.setData(data);
                refresh_teble_calc();
            });
    }
    function calculateProductSum(columnA, columnB) {
        let sum = 0;
        const rowData = table.getData(); // Fetch row data from Tabulator

        if (Array.isArray(rowData)) {
            // Ensure rowData is an array
            rowData.forEach((row) => {
                if (!isNaN(row[columnA]) && !isNaN(row[columnB])) {
                    const product =
                        parseFloat(row[columnA]) * parseFloat(row[columnB]);
                    sum += product; // Add the product to the sum
                }
            });
        } else {
            console.error(
                `rowData is not an array or is undefined for columns: ${columnA}, ${columnB}`
            );
        }

        return sum;
    }
    function calculateColumnSum(columnName) {
        let sum = 0;
        const rowData = cost_table.getData(); // Fetch row data from Tabulator

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
    function formatNumber(number) {
        // Ensure the number is parsed as a float and then format it
        return parseFloat(number).toLocaleString(undefined, { minimumFractionDigits: 3, maximumFractionDigits: 3 });
    }
    function calculateCostSum(columnA, columnB) {
        let sum = 0;
        const rowData = items_table.getData(); // Fetch row data from Tabulator

        if (Array.isArray(rowData)) {
            // Ensure rowData is an array
            rowData.forEach((row) => {
                if (!isNaN(row[columnA]) && !isNaN(row[columnB])) {
                    const product =
                        parseFloat(row[columnA]) * parseFloat(row[columnB]);
                    sum += product; // Add the product to the sum
                }
            });
        } else {
            console.error(
                `rowData is not an array or is undefined for columns: ${columnA}, ${columnB}`
            );
        }
        document.getElementById("item-cost-total").value = formatNumber(sum) + " دل ";

        return parseFloat(sum);
    }
    refresh_teble_calc();
    function refresh_teble_calc() {
        document.getElementById("cost-total").value = formatNumber(calculateColumnSum("cost_price"));

        document.getElementById("cost-dinar").value = formatNumber(calculateColumnSum("dinar_cost_price")) + " دل ";
    }
    const items_table = new Tabulator("#item-cost-table", {
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
            { title: "سعر التكلفة", field: "cost_unit_price", width: 90 },
            { title: "السعر", field: "dinar_unit_price", width: 90 },
            { title: "الكمية", field: "quantity", width: 90 },
            { title: "اسم الصنف", field: "name", width: 190 },
            { title: "رقم الصنف", field: "pno", width: 90 },
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
        .getElementById("cost-price")
        .addEventListener("change", function () {
            const cost_price = document.getElementById("cost-price").value;
            const rate = document.getElementById("exchange_rate").value;
            document.getElementById("cost-price-dinar").value =
                formatNumber((parseFloat(cost_price) * parseFloat(rate))) + " دل ";
        });

    document.getElementById("add-btn").addEventListener("click", function () {
        const invoice = getInputValue("invoice");
        const type = getSelectedText("type-name");
        const cost = getInputValue("cost-price");
        const rate = getInputValue("exchange_rate");
        const dinar = cleanNumericInput(getInputValue("cost-price-dinar"));

        const data = {
            invoice: invoice,
            type: type,
            cost: cost,
            rate: rate,
            dinar: dinar,
        };

        customFetch(`create-cost-record`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        })
            .then((response) => response.json())
            .then((result) => {
                console.log(result);
                alert("تمت اضافة بيان التكلفة");
                refreshCostsTable(invoice);
            })
            .catch((error) => {
                console.error("Error:", error);
            });
    });
    function getInputValue(id) {
        const element = document.getElementById(id);
        if (element) {
            if (element.type === "checkbox") {
                return element.checked;
            }
            return element.value;
        }
        return null;
    }
    function getSelectValue(id) {
        const selectElement = document.getElementById(id);
        return selectElement ? selectElement.value : "";
    }
    function getSelectedText(selectId) {
        const select = document.getElementById(selectId);
        return select && select.selectedIndex !== 0
            ? select.options[select.selectedIndex].text
            : "";
    }
    function cleanNumericInput(value) {
        return value.replace(/[^\d.-]/g, ""); // Remove any character that is not a digit, dot, or hyphen
    }
    document
        .getElementById("cost-btn")
        .addEventListener("click", function () {
            const cost_total = getInputValue("cost-total");
            const invoice_total = getInputValue("invoice-total");
            const invoice = getInputValue("invoice");

            const data = {
                cost_total: cost_total,
                invoice_total: invoice_total,
                invoice: invoice,
            };
            console.log(data);

            customFetch(`calculate-cost`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(data),
            })
                .then((response) => response.json())
                .then((result) => {
                    console.log(result);
                    alert("تم تحديث سعر التكلفة");
                    console.log("تم تحديث سعر التكلفة للفاتولرة رقم : ", invoice);
                    refreshItemsTable(invoice);
                })
                .catch((error) => {
                    console.error("Error:", error);
                });
        });
});
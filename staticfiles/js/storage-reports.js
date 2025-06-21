document.addEventListener("DOMContentLoaded", function () {


    // Fetch client ID from the URL query string
    const urlParams = new URLSearchParams(window.location.search);
    const clientid = urlParams.get("id"); // Retrieve the client ID from the URL (e.g., ?id=123)

    // Initialize Tabulator table
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
            { title: "رقم الي", field: "storageid", width: 90 },
            { title: "نوع الحساب", field: "account_type", width: 90 },
            { title: "نوع القيد", field: "transaction", width: 90 },
            { title: "طريقة الدفع", field: "payment", width: 90 },
            { title: "رقم الإيصال", field: "reciept_no", width: 90 },
            { title: "تاريخ القيد", field: "transaction_date", width: 90 },
            { title: "البند", field: "section", width: 90 },
            { title: "البند الفرعي", field: "subsection", width: 90 },
            { title: "اسم المستفيد", field: "person", width: 90 },
            { title: "القيمة", field: "amount", width: 90 },
            { title: "مقابل", field: "issued_for", width: 90 },
            { title: "ملاحظة", field: "note", width: 90 },
            { title: "المكان", field: "place", width: 90 },
            { title: "اعدت من قبل", field: "done_by", width: 90 },
            { title: "اسم المصرف", field: "bank", width: 90 },
            { title: "رقم الصك", field: "check_no", width: 90 },

            { title: "حالة اليومية", field: "daily_status", width: 90 },
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
        .getElementById("section")
        .addEventListener("change", function () {
            const sectionId = this.value;
            const subSectionSelect = document.getElementById("sub-section");

            // Clear previous options
            subSectionSelect.innerHTML =
                '<option value="" selected>اختر</option>';

            if (sectionId) {
                customFetch(`/get-subsections/?section_id=${sectionId}`, {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                    },
                })
                    .then((response) => response.json())
                    .then((data) => {
                        data.forEach((item) => {
                            const option = document.createElement("option");
                            option.value = item.autoid;
                            option.textContent = item.subsection;
                            subSectionSelect.appendChild(option);
                        });
                    })
                    .catch((error) =>
                        console.error("Error fetching subsections:", error)
                    );
            }
        });
    // Function to calculate the sum of a column in Tabulator
    function calculateColumnSum(columnName) {
        let sum = 0;
        const rowData = table.getData(); // Fetch row data from Tabulator

        if (Array.isArray(rowData)) {
            rowData.forEach((row) => {
                if (!isNaN(row[columnName])) {
                    sum += parseFloat(row[columnName]); // Convert to float and add to sum
                }
            });
        } else {
            console.error(`rowData is not an array for column: ${columnName}`);
        }

        return sum;
    }

    // Function to update input fields with formatted sum values
    function updateShowInput(selector, sum) {
        const input = document.getElementById(selector);
        if (input) {
            input.value =
                sum.toLocaleString("en-US", {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                }) + " دل";
        } else {
            console.warn(`Selector "${selector}" did not match any elements.`);
        }
    }

    function refreshShowInputs() {
        const totalAmountDeposit = calculateTransactionSum("ايداع"); // Calculate sum when transaction is "ايداع"
        const totalAmountWithdraw = calculateTransactionSum("صرف"); // Calculate sum when transaction is "صرف"

        const totalAmountDepositCash = calculateTransactionSum("ايداع", "نقدا"); // Calculate sum when transaction is "ايداع" and payment is "نقدا"
        const totalAmountDepositCheque = calculateTransactionSum("ايداع", "صك"); // Calculate sum when transaction is "ايداع" and payment is "صك"
        const realcash = totalAmountDepositCash - totalAmountWithdraw;

        console.log("ايداع", totalAmountDeposit);
        console.log("صرف", totalAmountWithdraw);
        console.log("ايداع نقدي", totalAmountDepositCash);
        console.log("ايداع صك", totalAmountDepositCheque);

        //Update input fields with calculated sums
        updateShowInput("deposit-total", totalAmountDeposit);
        updateShowInput("withdraw-total", totalAmountWithdraw);
        updateShowInput("cash-sum", totalAmountDepositCash);
        updateShowInput("check-sum", totalAmountDepositCheque);
        updateShowInput("real-cash", realcash);
    }

    function calculateTransactionSum(transactionType, paymentMethod = null) {
        let sum = 0;

        // Access rows in Tabulator
        const rows = table.getData(); // 'table' refers to your Tabulator instance

        rows.forEach((row) => {
            if (row.transaction === transactionType) {
                if (paymentMethod) {
                    if (row.payment === paymentMethod) {
                        sum += parseFloat(row.amount);
                    }
                } else {
                    sum += parseFloat(row.amount);
                }
            }
        });
        return sum;
    }

    // Function to fetch data from the API
    function fetchData() {
        const url = `api/get-all-storage`;

        customFetch(url, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        })
            .then((response) => response.json())
            .then((data) => {
                table.setData(data); // Load data into Tabulator
                refreshShowInputs(); // Recalculate and display column sums
            })
            .catch((error) => {
                console.error("Error fetching data:", error);
                alert("Failed to fetch account statement. Please try again later.");
            }).finally(() => {
                scrollToLastRow();
            });
    }
    fetchData();
    table.on("dataFiltered", function () {
        refreshShowInputs();
    });
    function exportToExcel() {
        table.download("xlsx", "table_data.xlsx"); // 'xlsx' is the file format
    }
    document
        .getElementById("export-btn-excel")
        .addEventListener("click", exportToExcel);
    document
        .getElementById("export-btn-pdf")
        .addEventListener("click", exportToPDF);
    // Example of vfs_fonts.js

    function exportToPDF() {
        // Get visible column field names
        let visibleColumns = table
            .getColumns() // Retrieve column components
            .filter((col) => col.isVisible()) // Check if the column is visible
            .map((col) => col.getField()); // Get the field names of visible columns

        // Filter table data based on visible columns
        let tableData = table.getData().map((row) => {
            // Create a new object with only visible fields
            return visibleColumns.reduce((filteredRow, field) => {
                filteredRow[field] = row[field]; // Copy value of visible field
                return filteredRow;
            }, {});
        });

        // Now `filteredData` contains only the visible columns from tableData
        console.log(tableData);

        // Sending the data to Django backend using fetch
        customFetch("/generate-pdf/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                data: tableData,
            }), // Send table data
        })
            .then((response) => response.blob())
            .then((blob) => {
                // Check if blob is a valid PDF
                const file = new Blob([blob], { type: "application/pdf" });
                const fileURL = URL.createObjectURL(file);

                // Open the PDF in a new window or download it
                const link = document.createElement("a");
                link.href = fileURL;
                link.download = "tabulator_data.pdf";
                link.click();
            })
            .catch((error) => {
                console.error("Error:", error);
            });
    }

    function applyFilters() {
        // Helper functions remain the same
        function getSelectedText(selectId) {
            const select = document.getElementById(selectId);
            return select && select.selectedIndex !== 0
                ? select.options[select.selectedIndex].text
                : "";
        }

        function getInputValue(inputId) {
            const input = document.getElementById(inputId);
            return input ? input.value.trim().toLowerCase() : "";
        }

        function getSelectedRadioValue(name) {
            const selectedRadio = document.querySelector(
                `input[name="${name}"]:checked`
            );
            return selectedRadio ? selectedRadio.value : null;
        }

        const filterValues = {
            client: getInputValue("cname"),
            fromdate: getInputValue("from-date"),
            todate: getInputValue("to-date"),
            account_detail: getInputValue("account-detail"),
            section: getSelectedText("section"),
            subsection: getSelectedText("sub-section"),
            type: getSelectedRadioValue("accountType"),
            transaction: getSelectedRadioValue("transaction-type"),
            payment: getSelectedRadioValue("payment"),
            place: getSelectedRadioValue("place"),
        };

        // Remove empty filters
        const activeFilters = Object.fromEntries(
            Object.entries(filterValues).filter(
                ([key, value]) => value !== null && value !== ""
            )
        );

        console.log("Active filter values:", activeFilters);

        // Check if no filters are active
        if (Object.keys(activeFilters).length === 0) {
            console.log("No active filters; fetching all data...");
            // Handle fetching all data here (send empty filters or default request)
            activeFilters.filter = "all"; // Example: Set to "all" for default behavior
        }

        // Get CSRF token
        function getCSRFToken() {
            const csrfInput = document.querySelector(
                "[name=csrfmiddlewaretoken]"
            );
            return csrfInput ? csrfInput.value : "";
        }

        customFetch("api/filter-all-storage", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify(activeFilters),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(
                        `Network error: ${response.status} ${response.statusText}`
                    );
                }
                return response.json();
            })
            .then((data) => {
                console.log("Filtered data:", data);
                table.replaceData(data); // Update Tabulator table
            })
            .catch((error) => {
                console.error("Error fetching filtered data:", error);
            }).finally(() => {
                scrollToLastRow();
            });
    }

    // Add event listeners to all filter inputs
    const inputIds = [
        "cname",
        "from-date",
        "to-date",
        "account-detail",
        "section",
        "sub-section",
    ];

    inputIds.forEach((inputId) => {
        const inputElement = document.getElementById(inputId);
        if (inputElement) {
            inputElement.addEventListener("input", applyFilters);
        }
    });

    // Add event listeners for radio buttons (grouped by name)
    const radioGroups = [
        "accountType",
        "transaction-type",
        "payment",
        "place",
    ];

    radioGroups.forEach((groupName) => {
        const radioButtons = document.querySelectorAll(
            `input[name="${groupName}"]` // Use backticks (`) instead of single or double quotes
        );
        radioButtons.forEach((radioButton) => {
            radioButton.addEventListener("change", applyFilters);
        });
    });

    document.getElementById("clear-btn").addEventListener("click", clearForm);
    function clearForm() {
        window.requestAnimationFrame(function () {
            const inputs = document.querySelectorAll(
                "input:not([name='csrfmiddlewaretoken']), select"
            );
            inputs.forEach(function (element) {
                if (!element.classList.contains("value-fixed")) {
                    if (
                        element.tagName.toLowerCase() === "input" ||
                        element.tagName.toLowerCase() === "textarea"
                    ) {
                        if (element.type === "checkbox" || element.type === "radio") {
                            element.checked = false; // Clear checkboxes and radio buttons
                        } else {
                            element.value = ""; // Reset other input types and textarea values
                        }
                    } else if (element.tagName.toLowerCase() === "select") {
                        element.selectedIndex = 0; // Reset select dropdowns
                    }
                }
            });
        });
    }
    function scrollToLastRow() {
        table.setPage(table.getPageMax()).then(() => {
            setTimeout(() => {
                // Scroll to last row
                var lastRow = table.getRows().pop();
                if (lastRow) {
                    table.scrollToRow(lastRow, "bottom").catch(err => console.warn("Scroll Error:", err));
                }

                // Scroll the table container to the bottom
                let tableContainer = document.getElementById("users-table");
                if (tableContainer) {
                    tableContainer.scrollTop = tableContainer.scrollHeight;
                }
            }, 300); // Small delay to ensure content loads before scrolling
        });
    }
});
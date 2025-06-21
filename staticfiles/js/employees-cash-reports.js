document.addEventListener('DOMContentLoaded', function () {
    function loadEditionsData(id) {
        fetch("/api/balance-editions-api/")
            .then(response => response.json())
            .then(data => {
                salaries_table.setData(data);
            })
            .catch(error => {
                console.error("Failed to fetch employee data:", error);
            }).finally(() => {
                calculateTotalAmount(salaries_table);
            });
    }
    function clearForm() {
        window.requestAnimationFrame(function () {
            const formElements = document.querySelectorAll("input, select, textarea");

            formElements.forEach(function (element) {
                if (!element.classList.contains("value-fixed")) {
                    const tag = element.tagName.toLowerCase();

                    if (tag === "input") {
                        if (element.type === "radio") {
                            element.checked = false; // Uncheck radio buttons
                        } else {
                            element.value = ""; // Reset other input values
                        }
                    } else if (tag === "textarea") {
                        element.value = ""; // Reset textarea values
                    } else if (tag === "select") {
                        element.selectedIndex = 0; // Reset select dropdowns
                    }
                }
            });

            loadEditionsData();
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        loadEditionsData();
    });
    document.getElementById("clear-btn").addEventListener("click", function () {
        clearForm();
    });
    const salaries_table = new Tabulator("#salaries-table", {
        data: [], // or use ajaxURL: '/your-endpoint' for dynamic data
        layout: "fitColumns",
        height: "100%",
        columns: [
            { title: "ر. المعاملة", field: "id" },
            { title: "التاريخ", field: "date", hozAlign: "center" },
            { title: "القيمة", field: "amount", hozAlign: "center", formatter: "money", formatterParams: { symbol: "د.ل", precision: 0 } },
            { title: "بيان التسوية", field: "description" },
            { title: "نوع التسوية", field: "type" },
        ],
        placeholder: "No Data Available",
    });
    // Combined filter function
    function applyFilters() {
        // Helper function to get selected text from a dropdown
        function getSelectedText(selectId) {
            const select = document.getElementById(selectId);
            return select && select.selectedIndex !== 0
                ? select.options[select.selectedIndex].text
                : "";
        }

        // Helper function to get trimmed and lowercased input value
        function getInputValue(inputId) {
            const input = document.getElementById(inputId);
            return input ? input.value.trim().toLowerCase() : "";
        }

        // Capture filter values dynamically
        const filterValues = {
            id: getInputValue("client"),
            fromdate: getInputValue("from-date"),
            todate: getInputValue("to-date"),
            type: document.querySelector('input[name="transactionType"]:checked')?.value || "",
        };

        console.log("Filter values:", filterValues);

        // Function to get CSRF token
        function getCSRFToken() {
            const csrfInput = document.querySelector(
                "[name=csrfmiddlewaretoken]"
            );
            return csrfInput ? csrfInput.value : "";
        }
        // Perform the fetch request
        customFetch("/api/filter/balance-editions-api/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify(filterValues),
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
                console.log("response: ", data);

                salaries_table.replaceData(data);

            })
            .catch((error) => {
                console.error("Error fetching filtered data:", error.message);
            }).finally(() => {
                calculateTotalAmount(salaries_table);
            });
    }

    // Add event listeners to all filter inputs
    const filterInputs = [
        "from-date",
        "to-date",
        "client",
        "credit",
        "debit",
        "none",
    ];

    filterInputs.forEach((inputId) => {
        document
            .getElementById(inputId)
            .addEventListener("input", () => {
                applyFilters();
            });
    });
    function calculateTotalAmount(table) {
        let total = 0;

        // Loop through all rows and sum the "amount" column
        table.getData().forEach(row => {
            let value = parseFloat(row.amount);
            if (!isNaN(value)) {
                total += value;
            }
        });

        // Set the total to the input field
        document.getElementById("dinar-total").value = total.toFixed(2);
    }
});
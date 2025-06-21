document.addEventListener('DOMContentLoaded', function () {
    // Initialize Tabulator
    const employees_table = new Tabulator("#employees-table", {
        layout: "fitColumns",
        height: "100%",
        selectable: 1,

        columns: [
            { title: "رقم الموظف", field: "employee_id", hozAlign: "center", width: 120 },
            { title: "اسم الموظف", field: "name", hozAlign: "right" },
            {
                title: "المرتب الشهري",
                field: "salary",
                hozAlign: "center",
                editor: "input",
                formatter: function (cell) {
                    let value = cell.getValue();
                    if (value == null || isNaN(value)) {
                        return "د.ل 0";
                    }
                    return `د.ل ${Number(value).toLocaleString()}`;
                }
            },
            {
                title: "الرصيد",
                field: "balance",
                hozAlign: "center",
                formatter: function (cell) {
                    let value = cell.getValue();
                    if (value == null || isNaN(value)) {
                        return "د.ل 0";
                    }
                    return `د.ل ${Number(value).toLocaleString()}`;
                }
            }
        ],
        placeholder: "No Data Available",

        rowClick: function (e, row) {
            selectedRow = row;
        }
    });

    // Load data
    function loadEmployeeData() {
        fetch("/api/employees-api")
            .then(response => response.json())
            .then(data => {
                employees_table.setData(data.results);
            })
            .catch(error => {
                console.error("Failed to fetch employee data:", error);
            });
    }
    function loadEditionsData(id) {
        fetch("/api/balance-editions/user/" + id)
            .then(response => response.json())
            .then(data => {
                salaries_table.setData(data);
            })
            .catch(error => {
                console.error("Failed to fetch employee data:", error);
            });
    }
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

                loadEmployeeData();
            });
        });
    }
    document.addEventListener("DOMContentLoaded", function () {
        loadEmployeeData();
    });
    document.getElementById("clear-btn").addEventListener("click", function () {
        clearForm();
    });
    const salaries_table = new Tabulator("#salaries-table", {
        data: [], // or use ajaxURL: '/your-endpoint' for dynamic data
        layout: "fitColumns",
        height: "100%",
        columns: [
            { title: "التاريخ", field: "date", hozAlign: "center" },
            { title: "القيمة", field: "amount", hozAlign: "center", formatter: "money", formatterParams: { symbol: "د.ل", precision: 0 } },
            { title: "بيان التسوية", field: "description" },
            { title: "نوع التسوية", field: "type" },
        ],
        placeholder: "No Data Available",
    });

    employees_table.on("rowClick", function (e, row) {
        console.log("Row clicked after data update:", row.getData());
        const employee_id = row.getData().employee_id; // Get pno of the clicked row
        console.log("Clicked employee_id:", employee_id);

        loadEditionsData(employee_id);
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
            fromdate: getInputValue("date"),
            todate: getInputValue("date"),
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
            });
    }

    // Add event listeners to all filter inputs
    const filterInputs = [
        "date",
        "client",
    ];

    filterInputs.forEach((inputId) => {
        document
            .getElementById(inputId)
            .addEventListener("input", () => {
                applyFilters();
            });
    });
});
document.addEventListener("DOMContentLoaded", function () {
    const urlParams = new URLSearchParams(window.location.search);
    const buyReturn = urlParams.get('buy_return');
    let value, value_name;
    if (buyReturn) {
        value = "source"
        value_name = "source_name"
    }
    else {
        value = "client"
        value_name = "client_name"
    }

    var return_table = new Tabulator("#return-table", {
        data: [], // Assign the data to the table
        layout: "fitColumns", // Adjust column widths to fit data
        columns: [
            { title: "رقم الاذن", field: "autoid", width: 100 },
            { title: "التاريخ", field: "date", width: 120 },
            { title: "عدد القطع", field: "quantity", width: 120 },
            { title: "الاجمالي", field: "amount", width: 150 },
            { title: "العميل", field: value, width: 120 },
            { title: "اسم العميل", field: value_name, width: 120 },
        ],
        movableColumns: true, // Allow columns to be moved
        resizableRows: true,  // Allow rows to be resized
        pagination: true,     // Enable pagination
        paginationSize: 5,   // Set number of rows per page
    });
    const element = document.getElementById("client");
    const choices = new Choices(element, {
        searchEnabled: true,
        removeItemButton: true, // Optional: allows removal of selected items
    });

    function fetchData() {
        // Fetch data from the API endpoint
        let url;
        if (buyReturn) {
            url = "/api/buy-permissions/";
        } else {
            url = "/permissions/";
        }
        console.log(buyReturn);
        customFetch(url, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        })
            .then(response => response.json()) // Parse JSON data from response
            .then(data => {
                // Initialize Tabulator with the fetched data
                console.log(data);
                return_table.setData(data.results);

            })
            .catch(error => {
                console.error('Error fetching data:', error);
            }).finally(() => {
                updateInput('total', calculateColumnSum('amount') + " دل ");
                scrollToLastRow();
            });
    }
    fetchData();
    function scrollToLastRow() {
        return_table.setPage(return_table.getPageMax()).then(() => {
            var lastRow = return_table.getRows().pop();
            if (lastRow) {
                return_table.scrollToRow(lastRow, "bottom").catch(err => console.warn("Scroll Error:", err));
            }
        });
    }
    function updateInput(id, value) {
        document.getElementById(id).value = value;
    }
    function calculateColumnSum(columnName) {
        const rowData = return_table.getData();  // Fetch row data from Tabulator
        console.log('rowdata: ', rowData);

        if (!Array.isArray(rowData)) {
            console.error(`rowData is not an array or is undefined for column: ${columnName}`);
            return 0;  // Return 0 if rowData is not an array
        }

        // Using reduce to sum the values
        return rowData.reduce((sum, row) => {
            const value = parseFloat(row[columnName]);
            return !isNaN(value) ? sum + value : sum;  // Only add to sum if value is a number
        }, 0);
    }
    function clearForm() {
        window.requestAnimationFrame(function () {
            const formElements = document.querySelectorAll(
                "input, select, textarea"
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
            });

            if (return_table) {
                return_table.clearFilter(); // Clear all filters applied
                fetchData();
                //console.log("Filters cleared");
            }
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
            client: getInputValue("client"),
            fromdate: getInputValue("from-date"),
            todate: getInputValue("to-date"),
            payment: getSelectedRadioValue("payment-status"),
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
        let url;
        if (buyReturn) {
            url = "/api/filter-return-requests/?buy_return=1";
        } else {
            url = "/api/filter-return-requests/";
        }

        customFetch(url, {
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
                return_table.replaceData(data); // Update Tabulator table
            })
            .catch((error) => {
                console.error("Error fetching filtered data:", error);
            }).finally(() => {
                scrollToLastRow();
            });
    }

    // Add event listeners to all filter inputs
    const inputIds = [
        "loan-radio",
        "cash-radio",
        "to-date",
        "payment_status_all",
        "client",
        "from-date",
    ];

    inputIds.forEach((inputId) => {
        const inputElement = document.getElementById(inputId);
        if (inputElement) {
            inputElement.addEventListener("change", applyFilters);
        }
    });
    return_table.on("rowClick", function (e, row) {
        console.log("Row clicked after data update:", row.getData());
        const clickedId = row.getData().autoid; // Get pno of the clicked row
        openWindow("/return-permissions/" + clickedId + "/profile/");
    });
    let childWindows = [];
    function openWindow(url, width = 600, height = 700) {
        // Get the parent window's dimensions and position
        const parentWidth = window.innerWidth;
        const parentHeight = window.innerHeight;
        const parentLeft = window.screenX;
        const parentTop = window.screenY;

        // Calculate the center position for the child window
        const left = parentLeft + (parentWidth - width) / 2;
        const top = parentTop + (parentHeight - height) / 2;

        // Open a new child window
        const childWindow = window.open(
            url,
            "_blank",
            `width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=yes`
        );

        if (!childWindow) {
            alert("Pop-up blocked! Please allow pop-ups for this website.");
            return;
        }

        /* // Set the child window's size and disable resizing by enforcing it every time it's resized
                      childWindow.addEventListener('resize', () => {
                        // Enforce fixed size by resetting the size after any resize attempt
                        childWindow.resizeTo(width, height);
                      });*/

        // Add the new child window to the array
        childWindows.push(childWindow);

        // Monitor the child window's state
        const monitorChild = setInterval(() => {
            if (childWindow.closed) {
                // Remove the closed window from the array
                childWindows = childWindows.filter((win) => win !== childWindow);
                clearInterval(monitorChild);
            }
        }, 300);

        /*// Focus all child windows periodically
                      setInterval(() => {
                        childWindows.forEach(win => {
                          if (!win.closed) {
                            win.focus();
                          }
                        });
                      }, 500);*/

        // Close all child windows when the parent is closed
        window.onbeforeunload = function () {
            childWindows.forEach((win) => {
                if (!win.closed) {
                    win.close();
                }
            });
        };
    }
    document.getElementById("clear-btn").addEventListener("click", function () {
        clearForm();
    });
    document.getElementById("print-btn").addEventListener("click", () => {
        const data = {
            label: "today_return_permission",
        };

        customFetch(`/api/print-dynamic-paper`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()  // <-- IMPORTANT for Django
            },
            body: JSON.stringify(data),
        })
            .then(response => response.text())  // <-- handle HTML or plain text
            .then(html => {
                const printWindow = window.open("", "_blank");
                printWindow.document.open();
                printWindow.document.write(html);
                printWindow.document.close();
            })
            .catch((error) => {
                console.error("Error fetching data:", error);
            });
    });
});
document.addEventListener("DOMContentLoaded", function () {
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
            {
                title: "تاريخ القيد",
                field: "registration_date",
                width: 100,
                formatter: function (cell) {
                    const value = cell.getValue();
                    if (value) {
                        const date = new Date(value); // Convert to a Date object
                        return date.toISOString().split("T")[0]; // Format as YYYY-MM-DD
                    }
                    return ""; // Return an empty string if value is invalid
                },
            }, // Registration Date
            { title: "رقم القيد", field: "autoid", width: 80 }, // Transaction ID
            { title: "نوع القيد", field: "transaction", width: 80 }, // Transaction
            {
                title: "دائن",
                field: "credit",
                width: 80,
                formatter: function (cell) {
                    const value = cell.getValue();
                    return !isNaN(value) ? parseFloat(value).toFixed(2) : value;
                },
            }, // Credit
            {
                title: "مدين",
                field: "debt",
                width: 80,
                formatter: function (cell) {
                    const value = cell.getValue();
                    return !isNaN(value) ? parseFloat(value).toFixed(2) : value;
                },
            }, // Debt

            { title: "بيان القيد", field: "details", width: 140 }, // Details

            {
                title: "تاريخ التسليم",
                field: "delivered_date",
                width: 100,
                formatter: function (cell) {
                    const value = cell.getValue();
                    if (value) {
                        const date = new Date(value); // Convert to a Date object
                        return date.toISOString().split("T")[0]; // Format as YYYY-MM-DD
                    }
                    return ""; // Return an empty string if value is invalid
                },
            }, // Delivered Date
            { title: "لحساب", field: "delivered_for", width: 90 }, // Delivered To
            {
                title: "الرصيد الحالي",
                field: "current_balance",
                width: 90,
                formatter: function (cell) {
                    const value = cell.getValue();
                    return !isNaN(value) ? parseFloat(value).toFixed(2) : value;
                },
            }, // Current Balance
        ],
        placeholder: "No Data Available", // Message when no data is present
        rowFormatter: function (row) {
            const rowData = row.getData();
            // Customize row formatting logic here if needed
        },
        rowClick: function (e, row) {
            const clickedPno = row.getData().pno; // Get pno of the clicked row
            console.log("Clicked Pno:", clickedPno);
        },
        tableBuilt: function () {
            console.log("Table has been built successfully.");
        },
    });

    // Fetch client ID from the URL query string
    const urlParams = new URLSearchParams(window.location.search);
    const clientid = urlParams.get("client") || urlParams.get("supplier"); // Retrieve the client ID from the URL (e.g., ?id=123)

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
    function getLastRowColumnValue(columnName) {
        const rowData = table.getData(); // Fetch all row data from Tabulator

        if (Array.isArray(rowData) && rowData.length > 0) {
            const lastRow = rowData[rowData.length - 1];
            return lastRow[columnName] !== undefined ? lastRow[columnName] : null;
        } else {
            console.error(`No data available or rowData is not an array for column: ${columnName}`);
            return null;
        }
    }
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
        const input = document.querySelector(selector);
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
    // Refresh the displayed sum inputs
    function refreshShowInputs() {
        const creditSum = calculateColumnSum("credit");
        const debtSum = calculateColumnSum("debt"); // Corrected from "dept"
        const balanceSum = getLastRowColumnValue("current_balance");
        const realBalance = creditSum - debtSum;

        // Update input fields with calculated sums
        updateShowInput("#credit-sum", creditSum);
        updateShowInput("#debt-sum", debtSum);
        updateShowInput("#balance-sum", parseFloat(balanceSum));
        updateShowInput("#real-balance", realBalance);
    }
    // Function to fetch data from the API
    function fetchData(clientid) {
        let url = ""; // Initialize URL variable
        if (urlParams.get("client")) {
            url = `/get-account-statement?id=${clientid}`;
        }
        if (urlParams.get("supplier")) {
            url = `/suppliers/get-account-statement?id=${clientid}`;
        }

        customFetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        }).then((response) => response.json())
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
    function exportToExcel() {
        table.download("xlsx", "table_data.xlsx"); // 'xlsx' is the file format
    }

    // Call fetchData if client ID is found in the URL
    if (clientid) {
        fetchData(clientid);
    } else {
        alert("Client ID not found in the URL.");
    }

    document.getElementById("export-btn-excel").addEventListener("click", exportToExcel);
    document.getElementById("export-btn-pdf").addEventListener("click", exportToPDF);

    table.on("rowClick", function (e, row) {
        console.log("Row clicked after data update:", row.getData());
        const details = row.getData().details; // Get pno of the clicked row
        const match = details.match(/فاتورة رقم (\d+)/);

        if (match) {
            const invoiceNumber = match[1];  // Extracted invoice number
            console.log("Invoice Number:", invoiceNumber);
            openWindow("/sell-invoice-profile/" + invoiceNumber + "/");
            /*if (details.includes("شراء")) {
                // If "شراء" is present, navigate to the profile page
                openWindow("/sell-invoice-profile/" + invoiceNumber + "/");
            }

            if (details.includes("ترجيع")) {
                // If "شراء" is present, navigate to the profile page
                openWindow("/return-permissions/" + invoiceNumber + "/profile/");
            }*/

        } else {
            console.log("Invoice number not found.");
        }
        console.log("Clicked details:", details);
    });
});



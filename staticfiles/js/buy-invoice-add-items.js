document.addEventListener("DOMContentLoaded", function () {

    get_invoice_items();
    function updateExchangeRate() {
        const currencyDropdown = document.getElementById("currency");
        const org_currency = document.getElementById("org-currency");

        const exchangeRateInput = document.getElementById("currency-rate");
        const selectedExchangeRate = parseFloat(currencyDropdown.value); // Convert value to a float
        if (isNaN(selectedExchangeRate)) {
            exchangeRateInput.value = "";
        } else {
            // Set the input value to the exchange rate formatted to 2 decimal places
            exchangeRateInput.value = selectedExchangeRate.toFixed(2);

            org_currency.value =
                currencyDropdown.options[
                    currencyDropdown.selectedIndex
                ].innerText.trim();
        }
    }

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
            { title: "رقم الي", field: "autoid", width: 90 },
            { title: "رقم خاص", field: "pno", width: 90 },
            { title: "الرقم الاصلي", field: "item_no", width: 90 },
            { title: "اسم الشركة", field: "company", width: 90 },
            { title: "رقم الشركة", field: "company_no", width: 90 },
            { title: "اسم الصنف", field: "name", width: 90 },
            { title: "سعر التوريد", field: "org_unit_price", width: 90 },
            { title: "سعر الشراء", field: "dinar_unit_price", width: 90 },
            { title: "الكمية", field: "quantity", width: 90 },
            { title: "سعر البيع", field: "current_buy_price", width: 90 },
            { title: "اقل سعر بيع", field: "current_less_price", width: 90 },
            { title: "مكان التخزين", field: "place", width: 90 },
            { title: "اجمالي س التوريد", field: "org_total_price", width: 90 },

            { title: "اجمالي ش بالدينار", field: "dinar_total_price", width: 90 },
            { title: "اجمالي ت بالدينار", field: "cost_total_price", width: 90 },

            {
                title: "رقم الفاتورة",
                field: "invoice_id",
                width: 90,
                visible: false,
            },
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
    function getCSRFToken() {
        return document.querySelector("[name=csrfmiddlewaretoken]").value;
    }
    /*// Add event listener to all radio buttons in the group
    table.on("rowClick", function (e, row) {
      console.log("Row clicked:", row.getData().autoid);
      const currencyDropdown = document.getElementById("currency");
      const currency =
        currencyDropdown.options[
          currencyDropdown.selectedIndex
        ].innerText.trim();
      const rate = document.getElementById("currency-rate").value;

      const data = {
        id: row.getData().autoid,
        currency: currency,
        rate: rate,
      };

      // Make a POST request to the server
      customFetch("/process-edit-invoice", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify(data),
      })
        .then((response) => {
          // Check if the response is a redirect (3xx status code)
          if (response.redirected) {
            // Open the new URL in a new window/tab
            openWindow(response.url);
            return;
          }

          // If the response is JSON, handle it accordingly
          return response.json();
        })
        .then((data) => {
          if (data) {
            console.log("Response from server:", data);
            if (data.success) {
              console.log("Invoice sent successfully!");
            } else {
              console.log("Error updating invoice:", data.message);
            }
          }
        })
        .catch((error) => {
          console.error("Error during fetch:", error);
          alert("An error occurred: " + error.message);
        });
    });*/

    let childWindows = [];

    function openWindow(url) {
        // Get the parent window's dimensions and position
        const parentWidth = window.innerWidth;
        const parentHeight = window.innerHeight;
        const parentLeft = window.screenX;
        const parentTop = window.screenY;

        // Calculate the center position for the child window
        const width = 600;
        const height = 700;
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


    document.getElementById("addProductsButton").addEventListener("click", function (event) {
        tempcheck = document.getElementById("temp-flag");
        const source = getSelectedText("source");
        const invoice = getInputValue("invoice-autoid");
        const date = getInputValue("invoice-date");
        const currency = getSelectedText("currency");
        const rate = getInputValue("currency-rate");
        const temp = tempcheck.checked ? 1 : 0;


        // Form is valid, proceed with submission
        event.preventDefault();
        const data = {
            source: source,
            invoice: invoice,
            date: date,
            currency: currency,
            rate: rate,
            temp: temp,
        };
        console.log(data);

        // Make a POST request to the server
        customFetch("/process-add-invoice", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify(data),
        })
            .then((response) => {
                // Check if the response is a redirect (3xx status code)
                if (response.redirected) {
                    // Open the new URL in a new window/tab
                    openWindow(response.url);
                    return;
                }

                // If the response is JSON, handle it accordingly
                return response.json();
            })
            .then((data) => {
                if (data) {
                    console.log("Response from server:", data);
                    if (data.success) {
                        console.log("Invoice sent successfully!");
                    } else {
                        console.log("Error updating invoice:", data.message);
                    }
                }
            })
            .catch((error) => {
                console.error("Error during fetch:", error);
                alert("An error occurred: " + error.message);
            });

    });
    // Helper function to get the value of an input field by ID
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

    document.getElementById("refresh").addEventListener("click", function () {
        get_invoice_items();
    });
    async function fetchInvoiceItems(invoiceId) {
        const url = `/fetch-buy-invoice-items?id=${encodeURIComponent(invoiceId)}`; // Replace `/your-endpoint-url/` with the actual endpoint path

        try {
            const response = await customFetch(url, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                },
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || "Failed to fetch invoice items");
            }

            const data = await response.json();
            console.log("Fetched items:", data); // You can remove this or handle the data as needed
            return data; // Return the fetched data
        } catch (error) {
            console.error("Error fetching invoice items:", error.message);
            return null; // You can handle errors differently, e.g., show a user-friendly message
        }
    }
    function get_invoice_items() {
        const invoice = parseFloat(
            document.getElementById("invoice-autoid").value.trim()
        );
        console.log("invioce", invoice);

        fetchInvoiceItems(invoice).then((items) => {
            if (items) {
                console.log("Invoice items:", items);
                table.replaceData(items); // Add the row data to second_table
                let totalPrice = calculateColumnSum("dinar_total_price"); // Get the column sum
                let totalcost = isNaN(calculateColumnSum("cost_total_price")) ? 0 : calculateColumnSum("cost_total_price");
                let netcost = totalcost == 0 ? 0 : totalcost - totalPrice;
                let roundedPrice = parseFloat(totalPrice).toFixed(2);
                document.getElementById("total").value = roundedPrice + " دل ";
                document.getElementById("expenses").value = parseFloat(netcost).toFixed(2) + " دل";
                document.getElementById("org-price").value =
                    calculateColumnSum("org_total_price").toFixed(2);
                let netTotal = totalPrice + netcost;
                document.getElementById("net-total").value = parseFloat(netTotal).toFixed(2) + " دل ";
                const paidValue = parseFloat(document.getElementById("paid").value);
                let remainingValue = isNaN(paidValue) ? netTotal : netTotal - paidValue;
                document.getElementById("remaining").value = parseFloat(remainingValue).toFixed(2) + " دل ";
                // Handle the fetched items, e.g., display them in the UI
            } else {
                console.log("No items fetched or an error occurred.");
                table.replaceData([]);
            }
        });
    }
    // Helper function to get the selected value of a select field by ID
    function getSelectValue(id) {
        const selectElement = document.getElementById(id);
        return selectElement ? selectElement.value : "";
    }
    function getSelectedText(selectId) {
        const select = document.getElementById(selectId);
        return select
            ? select.value
            : "";
    }
    // Get CSRF token
    function getCSRFToken() {
        const csrfInput = document.querySelector("[name=csrfmiddlewaretoken]");
        return csrfInput ? csrfInput.value : "";
    }
    // Main function to create a new record
    function createNewRecord() {
        // Collecting form data
        const data = {
            csrfmiddlewaretoken: getCSRFToken() || null,
            invoice_autoid: getInputValue("invoice-autoid") || null,
            org_invoice_id: getInputValue("org-invoice-id") || null,
            source: getSelectValue("source") || null,
            invoice_date: getInputValue("invoice-date") || null,
            arrive_date: getInputValue("arrive-date") || null,
            order_no: getInputValue("order-no") || null,
            currency: getSelectedText("currency") || null,
            currency_rate: getInputValue("currency-rate") || null,
            ready_date: getInputValue("ready-date") || null,
            reminder: getInputValue("reminder") || null,
            temp_flag: getInputValue("temp-flag") || 0,
            multi_source_flag: getInputValue("multi-source-flag") || 0,
        };

        console.log("Data to be sent:", data);

        // Sending the data to the API
        customFetch("api/create-buy-invoice-record", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(), // Ensure CSRF token is included
            },
            body: JSON.stringify(data),
        })
            .then((response) => {
                if (response.ok) {
                    document.getElementById("createButton").disabled = true; // Disable the button if successful
                    document.getElementById("cost-btn").disabled = false;
                    document.getElementById("source-btn").disabled = false;
                    document.getElementById("pay-btn").disabled = false;
                    document.getElementById("save-btn").disabled = false;
                    document.getElementById("excell-btn").disabled = false;
                    document.getElementById("addProductsButton").style.display = "block";
                    return true; // Return true if the response is successful
                } else {
                    alert("Error creating record.");
                    return false; // Return false if there's an error
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                return false; // Return false in case of any network error
            });
    }
    document
        .getElementById("cost-btn")
        .addEventListener("click", function (event) {
            form = document.getElementById("firstForm");

            const invoice = getInputValue("invoice-autoid");
            console.log(invoice);

            if (invoice) {
                // Form is valid, proceed with submission
                event.preventDefault();
                const data = {
                    invoice: invoice,
                };

                // Make a POST request to the server
                customFetch("/cost-management", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken(),
                    },
                    body: JSON.stringify(data),
                })
                    .then((response) => {
                        // Check if the response is a redirect (3xx status code)
                        if (response.redirected) {
                            // Open the new URL in a new window/tab
                            openWindow(response.url);
                            return;
                        }

                        // If the response is JSON, handle it accordingly
                        return response.json();
                    })
                    .then((data) => {
                        if (data) {
                            console.log("Response from server:", data);
                            if (data.success) {
                                console.log("Invoice sent successfully!");
                            } else {
                                console.log("Error updating invoice:", data.message);
                            }
                        }
                    })
                    .catch((error) => {
                        console.error("Error during fetch:", error);
                        alert("An error occurred: " + error.message);
                    });
            }
        });

    document
        .getElementById("excell-btn")
        .addEventListener("click", function (event) {
            const invoice = getInputValue("invoice-autoid");
            const org = getInputValue("org-invoice-id");
            const data = {
                invoice: invoice,
                org: org,
            };
            console.log(data);
            // Make a POST request to the server
            customFetch("/invoice_excell", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken(),
                },
                body: JSON.stringify(data),
            })
                .then((response) => {
                    // Check if the response is a redirect (3xx status code)
                    if (response.redirected) {
                        // Open the new URL in a new window/tab
                        openWindow(response.url);
                        return;
                    }

                    // If the response is JSON, handle it accordingly
                    return response.json();
                })
                .then((data) => {
                    if (data) {
                        console.log("Response from server:", data);
                        if (data.success) {
                            console.log("Invoice sent successfully!");
                        } else {
                            console.log("Error updating invoice:", data.message);
                        }
                    }
                })
                .catch((error) => {
                    console.error("Error during fetch:", error);
                    alert("An error occurred: " + error.message);
                });
        });

    document
        .getElementById("export-btn-excel")
        .addEventListener("click", exportToExcel);
    document
        .getElementById("export-btn-pdf")
        .addEventListener("click", exportToPDF);
    function exportToExcel() {
        table.download("xlsx", "lost&damaged_data.xlsx"); // 'xlsx' is the file format
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
                link.download = "lost&damaged_data.pdf";
                link.click();
            })
            .catch((error) => {
                console.error("Error:", error);
            });
    }
    document.getElementById("pay-btn").addEventListener("click", function (event) {
        event.preventDefault();
        openWindow('payment-installments');
    });
    window.addEventListener('storage', function (event) {
        if (event.key === 'refresh_sell_items' && event.newValue === 'true') {
            console.log('localStorage changed and flag is true:', event.newValue);

            get_invoice_items();  // your function to refresh data

            // Optional: reset the flag so it doesn't keep triggering
            localStorage.setItem('refresh_sell_items', 'false');
        }
    });
    document.getElementById("print-btn").addEventListener("click", () => {
        const data = {
            label: "specific_buy_invoice",
            invoice_no: document.getElementById("invoice-autoid").value,
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
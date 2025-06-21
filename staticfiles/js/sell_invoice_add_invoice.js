document.addEventListener("DOMContentLoaded", function () {
    const table = new Tabulator("#users-table", {
        height: "auto", // Adjust height or set a fixed height
        layout: "fitColumns",
        selectable: true,
        rowHeight: 20,
        movableColumns: true,
        columnHeaderVertAlign: "bottom",
        columnMenu: true, // Enable column menu
        data: [], // Placeholder, will be loaded dynamically
        columns: [
            // Column definitions
            { title: "رقم الي", field: "autoid", width: 90 },
            { title: "رقم خاص", field: "pno", width: 90 },
            { title: "اسم الشركة", field: "company", width: 90 },
            { title: "رقم الشركة", field: "company_no", width: 90 },
            { title: "اسم الصنف", field: "name", width: 90 },
            { title: "الكمية", field: "quantity", width: 90 },
            { title: "مستلم", field: "paid", width: 90 },
            { title: "باقي", field: "remaining", width: 90 },
            { title: "سعر البيع", field: "dinar_unit_price", width: 90 },
            { title: "الاجمالي", field: "dinar_total_price", width: 90 },
            { title: "ترجيع", field: "returned", width: 90 },
            { title: "*", field: "xx", width: 90 },

            {
                title: "رقم الفاتورة",
                field: "invoice_no",
                width: 90,
                visible: false,
            },
        ],
        placeholder: "No Data Available",
        rowFormatter: function (row) {
            // Set the height directly on each row
            row.getElement().style.height = "20px";

            var rowData = row.getData(); // Get the row data
            var itemvalue = parseInt(rowData.itemvalue); // Access specific column data
            var itemvalueb = parseInt(rowData.itemvalueb);
            var buyprice = parseFloat(rowData.buyprice); // Ensure buyprice is a number
            var costprice = parseFloat(rowData.costprice); // Ensure costprice is a number

            if (itemvalue == 0 && itemvalueb == 0) {
                row.getElement().style.backgroundColor = "red"; // Apply green row class
            }
            if (costprice > buyprice) {
                row.getElement().style.backgroundColor = "orange"; // Apply green row class
            }
            if (itemvalueb > 0) {
                row.getElement().style.backgroundColor = "green"; // Apply green row class
            }
            if (itemvalue < 0) {
                row.getElement().style.backgroundColor = "yellow"; // Apply green row class
            }

            // You can add more conditions as needed
        }, // Message when no data is present or after filtering
        rowClick: function (e, row) {
            //console.log("Row clicked", row);
            row.select(); // Select the clicked row
        },
        /*tableBuilt: function () {
          //console.log("table built");
          // After the table is built, set up column visibility handlers
          setupColumnVisibilityHandlers(table);

          // Set checkboxes based on column visibility
          table.getColumns().forEach((column) => {
            const columnField = column.getField();
            const checkbox = document.querySelector(
              `#column-menu input[value="${columnField}"]`
            );

            if (checkbox) {
              checkbox.checked = column.isVisible(); // Update checkbox based on column visibility
            }
          });
        },*/
    });
    fetchLastRecieptNo((nextRecieptNo) => {
        if (nextRecieptNo) {
            console.log(nextRecieptNo);
        } else {
            console.error("Failed to fetch next receipt number");
        }
    }); // Call the function if the value is 'ايداع'
    const element = document.getElementById("client");
    const choices = new Choices(element, {
        searchEnabled: true,
        removeItemButton: true, // Optional: allows removal of selected items
        addItems: true, // Allows adding items
        addChoices: true,
        duplicateItemsAllowed: false,
    });
    let allChoices = choices._store.choices.filter(choice => !choice.placeholder && !choice.disabled);
    let choices_options = allChoices.map(choice => choice.label.trim());
    console.log("choices_options at start:", choices_options);
    element.addEventListener("search", function () {
        // Get only visible choices (filtering out placeholders and removed items)
        let allChoices = choices._store.choices.filter(choice => !choice.placeholder && !choice.disabled);

        choices_options = allChoices.map(choice => choice.label.trim());

        //console.log("allChoices:", allChoices);
        console.log("choices_options:", choices_options);
    });

    element.addEventListener(
        "addItem",
        function (event) {
            const newClient = event.detail.label.trim();


            if (!choices_options.includes(newClient)) {
                const data = {
                    client_name: newClient,
                    account_type: "عميل",
                    sub_category: "NA",
                    types: "NA",
                    csrfmiddlewaretoken: getCSRFToken(),
                    other: "created by select element",
                    last_transaction: "0",
                };

                customFetch("/api/create-client", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken(),
                    },
                    body: JSON.stringify(data),
                })
                    .then((response) => response.json()) // Ensure response is properly handled
                    .then((data) => {
                        if (data && data.success) {
                            console.log("Client created successfully!");

                        } else {
                            console.log("Error occurred:", data.message);
                        }
                    })
                    .catch((error) => {
                        console.error("Error during fetch:", error);
                        alert("An error occurred: " + error.message);
                    });
            } else {
                console.log("Client already exists, skipping creation.");
            }

        },
        false
    );
    // Assuming you have a function to fetch the last reciept_no for the 'ايداع' transaction
    function fetchLastRecieptNo(callback) {
        customFetch(`get-last-sellinvoice-id`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then((data) => {
                const lastRecieptNo = parseFloat(data.autoid) || 0;
                const nextRecieptNo = lastRecieptNo + 1;

                // Set the value of the reciept-no input field
                document.getElementById("invoice-autoid").value = nextRecieptNo;

                // Invoke the callback with the computed value
                if (callback) callback(nextRecieptNo);
            })
            .catch((error) =>
                console.error("Error fetching reciept number:", error)
            );
    }
    document.addEventListener("DOMContentLoaded", function () {
        const today = new Date();
        const formattedDate = today.toISOString().split("T")[0]; // Format date as YYYY-MM-DD
        document.getElementById("invoice-date").value = formattedDate;
    });
    function calculateColumnSum(columnName) {
        let sum = 0;
        const rowData = table.getData(); // Fetch row data from Tabulator
        console.log("data: ", rowData);

        if (Array.isArray(rowData)) {
            // Ensure rowData is an array
            rowData.forEach((row, index) => {
                console.log(`Row ${index}:`, row);
                console.log(`Value in column ${columnName}:`, row[columnName]);
                if (!isNaN(row[columnName])) {
                    sum += parseFloat(row[columnName]); // Convert to float and add to sum
                }
            });
        } else {
            console.error(
                `rowData is not an array or is undefined for column: ${columnName}`
            );
        }
        console.log("column " + columnName + "sum= " + sum);
        return parseFloat(sum).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
    document
        .getElementById("createButton")
        .addEventListener("click", function (event) {
            form = document.getElementById("firstForm");
            const client = getSelectedText("client");
            const invoice = getInputValue("invoice-autoid");
            const date = getInputValue("invoice-date");

            // Get all input fields in the form
            const inputs = form.querySelectorAll("input[required]");
            const client_index = document.getElementById("client").selectedIndex;

            /*if (client_index == 0) {
              alert("الرجاء اختيار العميل");
              return;
            }*/
            // Loop through all required input fields
            inputs.forEach(function (input) {
                // Set custom validation message in Arabic
                if (!input.validity.valid) {
                    if (input.validity.valueMissing) {
                        input.setCustomValidity("هذا الحقل مطلوب");
                    } else {
                        input.setCustomValidity(""); // Reset the message
                    }
                }
            });

            if (form.checkValidity()) {
                // Form is valid, proceed with submission
                event.preventDefault();
                const data = {
                    client: client,
                    invoice: invoice,
                    date: date,
                };

                // Make a POST request to the server

                customFetch("/sell_invoice_add_items", {
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

                createNewRecord();
            } else {
                // Form is invalid, trigger the validation messages
                event.preventDefault();
                form.reportValidity();
                console.log("Form is invalid");
            }
        });

    document
        .getElementById("addProductsButton")
        .addEventListener("click", function (event) {
            form = document.getElementById("firstForm");
            const client = getSelectedText("client");
            const invoice = getInputValue("invoice-autoid");
            const date = getInputValue("invoice-date");

            // Get all input fields in the form
            const inputs = form.querySelectorAll("input[required]");
            const client_index = document.getElementById("client").selectedIndex;

            /*if (client_index == 0) {
              alert("الرجاء اختيار العميل");
              return;
            }*/
            // Loop through all required input fields
            inputs.forEach(function (input) {
                // Set custom validation message in Arabic
                if (!input.validity.valid) {
                    if (input.validity.valueMissing) {
                        input.setCustomValidity("هذا الحقل مطلوب");
                    } else {
                        input.setCustomValidity(""); // Reset the message
                    }
                }
            });

            if (form.checkValidity()) {
                // Form is valid, proceed with submission
                event.preventDefault();
                const data = {
                    client: client,
                    invoice: invoice,
                    date: date,
                };

                // Make a POST request to the server

                customFetch("/sell_invoice_add_items", {
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

            } else {
                // Form is invalid, trigger the validation messages
                event.preventDefault();
                form.reportValidity();
                console.log("Form is invalid");
            }
        });
    function updateInput(id, value) {
        document.getElementById(id).value = value;
    }
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
    // Get CSRF token
    function getCSRFToken() {
        const csrfInput = document.querySelector("[name=csrfmiddlewaretoken]");
        return csrfInput ? csrfInput.value : "";
    }
    // Main function to create a new record
    function createNewRecord() {
        const selectedValue = document.querySelector('input[name="payment"]:checked')?.value;

        // Display the result
        if (!selectedValue) {
            alert(" ! الرجاء اختيار طريقة الدفع! ");
        }
        // Collecting form data
        const data = {
            csrfmiddlewaretoken: getCSRFToken() || null,
            invoice_autoid: getInputValue("invoice-autoid") || null,
            client: getSelectValue("client") || null,
            client_rate: getSelectValue("rate") || null,
            client_category: getSelectValue("category") || null,
            client_limit: getSelectValue("limit") || null,
            client_balance: getSelectValue("balance") || null,
            invoice_date: getInputValue("invoice-date") || null,
            invoice_status: getInputValue("invoice-status") || null,
            payment_status: selectedValue,
            for_who: getInputValue("for-who") || null,
        };

        console.log("Data to be sent:", data);

        // Sending the data to the API
        customFetch("api/create-sell-invoice-record", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(), // Ensure CSRF token is included
            },
            body: JSON.stringify(data),
        })
            .then((response) => {
                if (response.ok) {
                    return response.json(); // Parse the response JSON into a JavaScript object
                } else {
                    alert("Error creating record.");
                    return Promise.reject("Error creating record."); // Reject the promise if response is not ok
                }
            })
            .then((data) => {
                // Now 'data' contains the parsed response JSON
                document.getElementById("createButton").disabled = true; // Disable the button if successful
                document.getElementById("save-btn").disabled = false;
                document.getElementById("addProductsButton").style.display = "block";
                document.getElementById("invoice-status").value = "لم تحضر"; // Set invoice-status to "لم تحضر"
                document.getElementById("balance").value = data.client_balance; // Set client balance in the input field
                return true; // Return true if the response is successful
            })
            .catch((error) => {
                console.error("Error:", error);
                return false; // Return false in case of any network error
            });
    }
    document.getElementById('client').addEventListener('change', function () {
        console.log("client");
        const selectedOption = this.options[this.selectedIndex];

        const rate = selectedOption.getAttribute('data-rate') || "NA";
        const category = selectedOption.getAttribute('data-subtype') || "NA";
        const loanLimit = selectedOption.getAttribute('data-loan-limit');
        const balance = selectedOption.getAttribute('data-balance');

        // Update the corresponding fields
        document.getElementById('rate').innerText = rate;
        document.getElementById('category').innerText = category;
        document.getElementById('limit').value = loanLimit;
        document.getElementById('balance').value = balance;
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
    window.openWindow = openWindow;

    document.getElementById("refresh-btn").addEventListener("click", function () {
        get_invoice_items();
    });
    function get_invoice_items() {
        const invoice = parseFloat(
            document.getElementById("invoice-autoid").value.trim()
        );
        console.log("invioce", invoice);

        fetchInvoiceItems(invoice).then((items) => {
            if (items) {
                console.log("Invoice items:", items);
                table.replaceData(items); // Add the row data to second_table
                // Handle the fetched items, e.g., display them in the UI
            } else {
                console.log("No items fetched or an error occurred.");
                table.replaceData([]);
            }
        }).finally(() => {
            const discount_per = document.getElementById("discount-percentage").checked;
            updateInput("total", calculateColumnSum("dinar_total_price") + " دل ");
            updateInput("returned", calculateColumnSum("returned"));
            updateInput("quantity", parseInt(calculateColumnSum("quantity")));
            const total = parseFloat(document.getElementById("total")?.value.replace(/[^\d.]/g, '')) || 0;
            const discount_value = parseFloat(document.getElementById("discount")?.value) || 0
            const discount = discount_per ? (discount_value / 100) * total : discount_value;
            const returned = parseFloat(document.getElementById("returned")?.value) || 0;
            const paid = parseFloat(document.getElementById("paid")?.value) || 0;
            const netPrice = total - discount - returned;
            const remaining = netPrice - paid;
            updateInput("net-total", netPrice + " دل ");
            updateInput("remaining", remaining + " دل ");
        });
    }
    async function fetchInvoiceItems(invoiceId) {
        const url = `/fetch-sell-invoice-items?id=${encodeURIComponent(invoiceId)}`; // Replace `/your-endpoint-url/` with the actual endpoint path

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

    document.getElementById("paid").addEventListener("change", function () {
        const netTotal = parseFloat(document.getElementById("net-total")?.value) || 0;
        const paid = parseFloat(document.getElementById("paid")?.value) || 0;
        const remaining = netTotal - paid;
        updateInput("remaining", remaining + " دل ");
    })
    document.getElementById("returned").addEventListener("change", function () {
        update_net_total();
    })
    document.getElementById("discount").addEventListener("change", function () {
        update_net_total();
    })
    document.getElementById("discount-percentage").addEventListener("change", function () {
        const discount_per = document.getElementById("discount-percentage").checked;
        document.getElementById("discount-curr").value = discount_per ? " % " : " دل ";
        update_net_total();
    })

    function update_net_total() {
        const discount_per = document.getElementById("discount-percentage").checked;
        console.log("percentage: ", discount_per);
        const total = parseFloat(document.getElementById("total")?.value.replace(/[^\d.]/g, '')) || 0;
        const discount_value = parseFloat(document.getElementById("discount")?.value) || 0
        const discount = discount_per ? (discount_value / 100) * total : discount_value;
        const returned = parseFloat(document.getElementById("returned")?.value) || 0;
        const netPrice = total - discount - returned;
        updateInput("net-total", netPrice + " دل ");
    }
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
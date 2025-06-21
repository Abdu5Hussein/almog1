document.addEventListener("DOMContentLoaded", function () {

    let today = new Date().toISOString().split("T")[0];
    document.getElementById("filter-date").value = today;
    document.getElementById("transaction-date").value = today;

    /*document.getElementById("other").addEventListener("change", function () {
      if (this.checked) {
        const select = document.getElementById("for-who");
        let found = false;

        for (let i = 0; i < select.options.length; i++) {
            if (select.options[i].text.trim() === "مصاريف اخرى") {
                const value = select.options[i].value;

                choices.setChoiceByValue(value); // This is the correct method
                found = true;
                choices.disable();

                console.log("Option 'مصاريف اخرى' selected");
                console.log("Option with id", choices.getValue().value);
                break;
            }
        }

        // Optional: Add the option if it doesn't exist
        if (!found) {
          const newOption = new Option("مصاريف اخرى", "other-expense");
          select.add(newOption);
          select.selectedIndex = select.options.length - 1;
        }

        // Optional: trigger a change event if needed
        select.dispatchEvent(new Event("change"));
      }
    });*/
    const categoryRadios = document.getElementsByName("category");
    categoryRadios.forEach((radio) => {
        radio.addEventListener("change", () => {
            const categoryRadioId = radio.id; // Get the value of the selected radio button
            if (categoryRadioId == "other") {
                if (radio.checked) {
                    const select = document.getElementById("for-who");
                    let found = false;

                    for (let i = 0; i < select.options.length; i++) {
                        if (select.options[i].text.trim() === "مصاريف اخرى") {
                            const value = select.options[i].value;

                            choices.setChoiceByValue(value); // This is the correct method
                            found = true;
                            choices.disable();

                            console.log("Option 'مصاريف اخرى' selected");
                            console.log("Option with id", choices.getValue().value);
                            break;
                        }
                    }

                    // Optional: Add the option if it doesn't exist
                    if (!found) {
                        const newOption = new Option("مصاريف اخرى", "other-expense");
                        select.add(newOption);
                        select.selectedIndex = select.options.length - 1;
                    }

                    // Optional: trigger a change event if needed
                    select.dispatchEvent(new Event("change"));
                }
            }
            else if (categoryRadioId == "source") {
                if (radio.checked) {
                    console.log("Source category selected");
                }
            }
            else {
                choices.enable();
            }
        });
    });
    //const form = document.getElementById("myForm");
    const withdrawRadios = document.getElementsByName("transaction-type");
    const reciept_no = document.getElementById("reciept-no");

    // Add event listener to all radio buttons in the group
    withdrawRadios.forEach((radio) => {
        radio.addEventListener("change", () => {
            const withdrawRadioValue = radio.value; // Get the value of the selected radio button
            if (withdrawRadioValue === "ايداع") {
                fetchLastRecieptNo("ايداع", (nextRecieptNo) => {
                    if (nextRecieptNo) {
                        reciept_no.value = nextRecieptNo;
                    } else {
                        console.error("Failed to fetch next receipt number");
                        reciept_no.value = "Error"; // Optional: indicate an error in the input field
                    }
                }); // Call the function if the value is 'ايداع'
            } else if (withdrawRadioValue === "صرف") {
                fetchLastRecieptNo("صرف", (nextRecieptNo) => {
                    if (nextRecieptNo) {
                        reciept_no.value = nextRecieptNo;
                    } else {
                        console.error("Failed to fetch next receipt number");
                        reciept_no.value = "Error"; // Optional: indicate an error in the input field
                    }
                }); // Call the function if the value is 'ايداع'// Do nothing if the value is 'صرف'
            }
        });
    });
    // Assuming you have a function to fetch the last reciept_no for the 'ايداع' transaction
    function fetchLastRecieptNo(type = "ايداع", callback) {
        customFetch(`api/get-last-reciept-no?transactionType=${type}`, {
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
                const lastRecieptNo = parseFloat(data.lastRecieptNo) || 0;
                const nextRecieptNo = lastRecieptNo + 1;

                // Set the value of the reciept-no input field
                document.getElementById("reciept-no").value = nextRecieptNo;

                // Invoke the callback with the computed value
                if (callback) callback(nextRecieptNo);
            })
            .catch((error) =>
                console.error("Error fetching reciept number:", error)
            );
    }

    // Initialize Tabulator
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
            { title: "رقم المعاملة", field: "storageid", width: 90 },
            { title: "نوع الحساب", field: "account_type", width: 90 },
            { title: "المعاملة", field: "transaction", width: 90 },
            { title: "تاريخ المعاملة", field: "transaction_date", width: 90 },
            { title: "رقم الإيصال", field: "reciept_no", width: 90 },
            { title: "المكان", field: "place", width: 90 },
            { title: "القسم", field: "section", width: 90 },
            { title: "الفرع", field: "subsection", width: 90 },
            { title: "الشخص المعني", field: "person", width: 90 },
            { title: "المبلغ", field: "amount", width: 90 },
            { title: "أصدر من أجل", field: "issued_for", width: 90 },
            { title: "ملاحظة", field: "note", width: 90 },
            { title: "طريقة الدفع", field: "payment", width: 90 },
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
    refreshTable();
    function refreshTable() {
        customFetch("api/get-today-storage", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        })
            .then((response) => response.json())
            .then((data) => {
                console.log("Fetched Data:", data);

                // Set data in Tabulator
                table.setData(data);
            })
            .catch((error) => console.error("Error fetching data:", error)).finally(() => {
                scrollToLastRow();
            });
    }
    table.on("rowClick", function (e, row) {
        console.log("Row clicked after data update:", row.getData());
        const id = row.getData().storageid; // Get pno of the clicked row
        sessionStorage.setItem("storageid", id);
        const rowData = row.getData();
        //populateInputFields(rowData);
        console.log("Clicked id:", id);
    });
    function populateInputFields(data) {
        // For 'countries' dropdown (set selected item based on 'data.itemsize')
        const placeSelect = document.getElementById("currency");
        const currencyOptions = placeSelect.options;
        let currencySelected = false; // Flag to track if a match is found
        for (let i = 0; i < currencyOptions.length; i++) {
            if (currencyOptions[i].text === data.accountcurr) {
                // Compare text (country name)
                placeSelect.selectedIndex = i; // Set the selected option
                currencySelected = true; // Mark as selected
                break;
            }
        }
        if (!currencySelected) {
            // Reset if no match found
            placeSelect.selectedIndex = 0; // Set the selected option to the first one
        }

        // For 'item-main' dropdown (set selected item based on 'data.itemmain')
        const subSelect = document.getElementById("sub-category");
        const subOptions = subSelect.options;
        let subSelected = false; // Flag to track if a match is found
        for (let i = 0; i < subOptions.length; i++) {
            if (subOptions[i].text === data.category) {
                // Compare text (item main)
                subSelect.selectedIndex = i; // Set the selected option
                subSelected = true; // Mark as selected
                break;
            }
        }
        if (!subSelected) {
            // Reset if no match found
            subSelect.selectedIndex = 0; // Set the selected option to the first one
        }

        // For 'item-sub-main' dropdown (set selected item based on 'data.itemsubmain')
        const daySelect = document.getElementById("installments");
        const dayOptions = daySelect.options;
        let daySelected = false; // Flag to track if a match is found
        for (let i = 0; i < dayOptions.length; i++) {
            if (dayOptions[i].text === data.loan_day) {
                // Compare text (item sub main)
                daySelect.selectedIndex = i; // Set the selected option
                daySelected = true; // Mark as selected
                break;
            }
        }
        if (!daySelected) {
            // Reset if no match found
            daySelect.selectedIndex = 0; // Set the selected option to the first one
        }

        // For 'company' dropdown (set selected item based on 'data.companyproduct')
        const typeSelect = document.getElementById("types");
        const typeOptions = typeSelect.options;
        let typeSelected = false; // Flag to track if a match is found
        for (let i = 0; i < typeOptions.length; i++) {
            if (typeOptions[i].text === data.subtype) {
                // Compare text (company name)
                typeSelect.selectedIndex = i; // Set the selected option
                typeSelected = true; // Mark as selected
                break;
            }
        }
        if (!typeSelected) {
            // Reset if no match found
            typeSelect.selectedIndex = 0; // Set the selected option to the first one
        }

        if (data.type == "عميل") {
            document.getElementById("client").checked = true; // Use 'checked' for radio buttons
        } else if (data.type == "مورد") {
            document.getElementById("source").checked = true; // Use 'checked' for radio buttons
        }

        if (data.client_stop == 1) {
            document.getElementById("client-stop").checked = true; // Use 'checked' for radio buttons
        } else {
            document.getElementById("client-stop").checked = false; // Use 'checked' for radio buttons
        }

        if (data.curr_flag == 1) {
            document.getElementById("account-type").checked = true; // Use 'checked' for radio buttons
        } else {
            document.getElementById("account-type").checked = false; // Use 'checked' for radio buttons
        }

        if (data.permissions && data.permissions.includes("sales")) {
            document.getElementById("sales").checked = true; // Check if 'sales' is in permissions
        } else {
            document.getElementById("sales").checked = false; // Uncheck if 'sales' is not in permissions
        }

        if (data.permissions && data.permissions.includes("purchases")) {
            document.getElementById("purchases").checked = true; // Check if 'sales' is in permissions
        } else {
            document.getElementById("purchases").checked = false; // Uncheck if 'sales' is not in permissions
        }

        if (data.permissions && data.permissions.includes("stock")) {
            document.getElementById("stock").checked = true; // Check if 'sales' is in permissions
        } else {
            document.getElementById("stock").checked = false; // Uncheck if 'sales' is not in permissions
        }

        if (data.permissions && data.permissions.includes("client-reports")) {
            document.getElementById("client-reports").checked = true; // Check if 'sales' is in permissions
        } else {
            document.getElementById("client-reports").checked = false; // Uncheck if 'sales' is not in permissions
        }

        document.getElementById("cname-arabic").value = data.name || "";
        document.getElementById("cno").value = data.clientid || "";
        document.getElementById("address").value = data.address || "";
        document.getElementById("phone-no").value = data.phone || "";
        document.getElementById("mobile-no").value = data.mobile || "";
        document.getElementById("email").value = data.email || "";
        document.getElementById("website").value = data.website || "";
        document.getElementById("last-history").value =
            data.last_transaction || "";
        document.getElementById("limit").value = data.loan_period || "";
        document.getElementById("limit-value").value = data.loan_limit || "";
        document.getElementById("text-area").value = data.other || "";
    }
    // Function to get CSRF token
    function getCSRFToken() {
        return document.querySelector("[name=csrfmiddlewaretoken]").value;
    }

    document
        .getElementById("clear-btn")
        .addEventListener("click", clearForm);
    function clearForm() {
        window.requestAnimationFrame(function () {
            const formElements = document.querySelectorAll(
                "form input, form select, form textarea"
            );
            formElements.forEach(function (element) {
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

    const element = document.getElementById("for-who");
    const choices = new Choices(element, {
        searchEnabled: true,
        removeItemButton: true, // Optional: allows removal of selected items
        addItems: true, // Allows adding items
        addChoices: true,
        duplicateItemsAllowed: false,
    });
    element.addEventListener(
        "addItem",
        function (event) {
            // do something creative here...
            console.log(event.detail.id);
            console.log(event.detail.value);
            console.log(event.detail.label);
            console.log(event.detail.customProperties);
            console.log(event.detail.groupValue);
        },
        false
    );
    // Add event listeners to checkboxes (should run on page load)
    document
        .querySelectorAll(".checkbox-form input[type='checkbox']")
        .forEach((checkbox) => {
            checkbox.addEventListener("change", updatePermissions);
        });
    document
        .getElementById("createButton")
        .addEventListener("click", function (event) {
            createNewRecord();
            clearForm();
        });
    function createNewRecord() {
        const data = {
            csrfmiddlewaretoken: getCSRFToken(),
            reciept_no: getValueById("reciept-no"),
            transaction_date: getValueById("transaction-date"),
            amount: parseFloat(getValueById("amount")) || 0,
            for_what: getValueById("for-what"),
            note: getValueById("note"),

            type: getCheckedRadioValue("category"),        // name="account-type"
            transaction: getCheckedRadioValue("transaction-type"),  // name="transaction"
            pay_method: getCheckedRadioValue("payment"),    // name="pay-method"

            daily: getCheckedRadioValue("daily"),

            place: getSelectedTextById("place"),
            section: getSelectedTextById("section"),
            subsection: getSelectedTextById("sub-section"),
            for_who: choices.getValue().label,

            bank: getValueById("bank"),
            checkno: getValueById("check-no"),
        };

        console.log("Data to be sent:", data);
        customFetch("api/create-storage-record", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify(data),
        }).then((response) => {
            if (response.ok) {
                alert("Record created successfully!");
                refreshTable();
            } else {
                alert("Error creating record.");
                console.log(getCSRFToken());
            }
        }).catch((error) => console.error("Error:", error));

    }


    document
        .getElementById("deleteButton")
        .addEventListener("click", function (event) {
            deleteRecord();
        });
    function deleteRecord() {
        id = sessionStorage.getItem("storageid");
        if (!id) {
            alert("اختر سجل لحذفه");
            return;
        }

        const confirmation = window.confirm(
            "هل أنت متأكد من أنك تريد حذف هذا السجل؟"
        );
        if (!confirmation) {
            return;
        }

        const data = {
            csrfmiddlewaretoken: getCSRFToken(),
            storage_id: id,
        };

        customFetch("api/delete-storage-record", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(), // Add the CSRF token here
            },
            body: JSON.stringify(data),
        })
            .then((response) => {
                if (response.ok) {
                    alert("Record deleted successfully!");
                    refreshTable();
                } else {
                    alert("Error deleting record.");
                    console.log(getCSRFToken()); // Check the value of the CSRF token
                }
            })
            .catch((error) => console.error("Error:", error));
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
            return selectedRadio ? selectedRadio.id : null;
        }

        const filterValues = {
            fromdate: getInputValue("filter-date"),
            todate: getInputValue("filter-date"),
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
            });
    }

    // Add event listeners to all filter inputs
    const filterInputs = ["filter-date"];

    filterInputs.forEach((inputId) => {
        document
            .getElementById(inputId)
            .addEventListener("input", applyFilters);
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
    document
        .getElementById("check")
        .addEventListener("change", function () {
            // If #check is checked, show #check-container
            if (this.checked) {
                document.getElementById("check-container").style.display =
                    "block";
            } else {
                // If #check is unchecked, hide #check-container
                document.getElementById("check-container").style.display = "none";
            }
        });
    document.getElementById("cash").addEventListener("change", function () {
        // If #check is checked, show #check-container
        if (this.checked) {
            document.getElementById("check-container").style.display = "none";
        }
    });

    document
        .getElementById("print-btn")
        .addEventListener("click", function () {
            window.open('/print/today-treasury-statement/', '_blank');
        });

    function printTabulatorTable() {
        // Clone the table for printing
        const tableClone = document
            .getElementById("users-table")
            .cloneNode(true);

        // Create a new window for printing
        const printWindow = window.open("", "", "height=900,width=800");

        // Get today's date in yyyy/mm/dd format
        const todayDate = new Date().toISOString().split("T")[0]; // Format: YYYY-MM-DD

        // Add print styles and content
        const printStyles = `
                  <style>
                      body {
                          font-family: Arial, sans-serif;
                          margin: 0;
                          padding: 20px;
                      }
                      .header {
                          text-align: center;
                          margin-bottom: 20px;
                      }
                      .logo {
                          width: 100px;
                          height: auto;
                      }
                      .company-name {
                          font-size: 24px;
                          font-weight: bold;
                          margin-top: 10px;
                      }
                      .date {
                          font-size: 16px;
                          margin-top: 5px;
                      }
                      .table-container {
                          margin-top: 30px;
                          border: 1px solid #ddd;
                          padding: 10px;
                      }
                      table {
                          width: 100%;
                          border-collapse: collapse;
                          margin-top: 20px;
                      }
                      th, td {
                          padding: 12px;
                          text-align: left;
                          border: 1px solid #ddd;
                      }
                      th {
                          background-color: #f2f2f2;
                          color: #333;
                      }
                      .signature-section {
                          margin-top: 40px;
                          display: flex;
                          justify-content: space-between;
                          font-size: 16px;
                      }
                      .signature-line {
                          border-bottom: 1px solid #000;
                          width: 200px;
                          height: 20px;
                          margin-top: 5px;
                      }
                      .footer {
                          text-align: center;
                          font-size: 12px;
                          margin-top: 50px;
                      }
                      /* Hide elements not needed for print */
                      .no-print {
                          display: none;
                      }
                  </style>
                `;

        const printContent = `
                  <div class="header">
                      <img src="your-logo-path.jpg" alt="Company Logo" class="logo">
                      <div class="company-name">Almog Oil</div>
                      <div class="date">Date: ${todayDate}</div>
                  </div>
                  ${printStyles}
                  <div class="table-container">
                      <table>
                          ${tableClone.outerHTML}
                      </table>
                  </div>
                  <div class="signature-section">
                      <div>
                          <div>Client Signature:</div>
                          <div class="signature-line"></div>
                      </div>
                      <div>
                          <div>Customer Signature:</div>
                          <div class="signature-line"></div>
                      </div>
                  </div>
                  <div class="footer">
                      Printed on: ${todayDate}
                  </div>
                  `;

        // Write the content to the print window
        printWindow.document.write(printContent);

        // Close the document and trigger the print dialog
        printWindow.document.close();
        printWindow.print();
    }
    let childWindows = [];
    document
        .getElementById("section-open")
        .addEventListener("click", function () {
            openWindow("sections-and-subsections");
        });
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
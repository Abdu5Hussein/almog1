document.addEventListener("DOMContentLoaded", function () {
    // Initialize Tabulator
    const table = new Tabulator("#users-table", {
        index: "fileid", // Use "fileid" as the unique row identifier
        height: "auto", // Adjust height or set a fixed height
        layout: "fitColumns",
        selectable: true,
        columnHeaderVertAlign: "bottom",
        data: [], // Placeholder, will be loaded dynamically
        columns: [
            {
                title: "رقم العميل",
                field: "clientid",
                sorter: "number",
                visible: true,
                width: 150,
            },
            {
                title: "اسم العميل",
                field: "name",
                sorter: "string",
                visible: true,
                width: 400,
            },
            {
                title: "الرصيد",
                field: "balance",
                sorter: "string",
                visible: true,
                width: 300,
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
    refreshTable();

    function refreshTable({ page = 1, size = 100 } = {}) {
        console.time("fetchData"); // Start timer
        customFetch(`api/get-all-clients?page=${page}&size=${size}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
            .then((response) => response.json())
            .then((data) => {
                console.log("Fetched Data:", data);
                active_url = "server_Data_No_Filter";
                console.log("active_url for pagination:", active_url);
                //console.log("page:", page);

                console.time("tableTime");
                //console.log("sort status: ", table.getDataCount());
                if (page === 1) {
                    // For the first page, replace the existing data
                    table.setData(data.data);
                    console.log("data set to the table");
                    //console.log("getDataCount: ", table.getDataCount());
                    currentPage = 1;
                } else {
                    let scrollPosition = tableContainer.scrollTop; // Save scroll position
                    //let currentData = table.getData();  // Get current table data
                    //let combinedData = currentData.concat(data.data);  // Combine existing data with new data
                    table.addData(data.data);
                    tableContainer.scrollTop = scrollPosition;
                    console.log("data added to the table");
                    //console.log("getDataCount: ", table.getDataCount());
                }
                console.timeEnd("tableTime");

                // Update lastPage flag
                lastPage = data.page_no == data.last_page ? true : false;
                console.time("PaginationTime");
                updatePagination(data.last_page, data.page_no);
                console.timeEnd("PaginationTime");


                return data; // Return data for further processing
            })
            .catch((error) => console.error("Error fetching data:", error)).finally(() => {
                console.timeEnd("fetchData"); // End the timer regardless of success or failure
                isLoading = false; // Reset loading flag after fetch completes
                hideLoader();
            });
    }
    table.on("rowClick", function (e, row) {
        console.log("Row clicked after data update:", row.getData());
        const id = row.getData().clientid; // Get pno of the clicked row
        const rowData = row.getData();
        populateInputFields(rowData);
        console.log("Clicked id:", id);
    });

    const element = document.getElementById("types");
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

    function populateInputFields(data) {
        // Manually define the mapping of tname to fileid
        const types = {
            قطاعي: "1",
            جملة: "2",
            مسوق: "3",
            تسويق: "4",
            "القائمة السوداء": "5",
        };

        // Function to set dropdown selection based on tname value
        function setDropdownSelectionWithChoices(
            choicesInstance,
            valueToMatch
        ) {
            try {
                // Get the ID based on the tname value
                const idToMatch = types[valueToMatch];

                if (idToMatch) {
                    const success = choicesInstance.setChoiceByValue(idToMatch); // Set the value in the dropdown

                    if (success) {
                        console.log(`Selection updated to value: ${idToMatch}`);
                    } else {
                        console.warn(
                            `Value '${idToMatch}' not found in the choices.`
                        );
                    }
                } else {
                    choicesInstance.removeActiveItems();
                    console.log(
                        "No matching fileid found for tname, selection cleared."
                    );
                }
            } catch (error) {
                console.error("Error setting dropdown selection:", error);
            }

            // Debugging log to see available choices
            console.log(
                "Available choices:",
                choicesInstance._store.choices.map((choice) => choice.value)
            );
            console.log("value: ", valueToMatch);
        }

        function setDropdownSelection(dropdownId, valueToMatch) {
            const dropdown = document.getElementById(dropdownId);
            const options = dropdown.options;
            let matchFound = false;

            for (let i = 0; i < options.length; i++) {
                if (
                    options[i].value === valueToMatch ||
                    options[i].text === valueToMatch
                ) {
                    dropdown.selectedIndex = i; // Set the matching option
                    matchFound = true;
                    break;
                }
            }

            if (!matchFound) {
                dropdown.selectedIndex = 0; // Reset to the first option if no match
            }
        }
        // Populate dropdowns
        setDropdownSelection("currency", data.accountcurr);
        setDropdownSelection("sub-category", data.category);
        setDropdownSelection("installments", data.loan_day);

        setDropdownSelectionWithChoices(choices, data.subtype);

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
        .getElementById("new-record-button")
        .addEventListener("click", function (event) {
            createNewRecord();
        });

    // Initialize a permissions string
    let permissions = "";

    // Function to update permissions based on checkbox state
    function updatePermissions() {
        // Collect all checkboxes
        const checkboxes = document.querySelectorAll(
            ".checkbox-form input[type='checkbox']"
        );

        // Reset permissions string
        permissions = "";

        // Loop through checkboxes to build the permissions string
        checkboxes.forEach((checkbox) => {
            if (checkbox.checked) {
                permissions += checkbox.id + ";"; // Append checked checkbox ID
            }
        });

        console.log("Updated Permissions:", permissions); // Log the updated permissions
    }

    // Add event listeners to checkboxes (should run on page load)
    document
        .querySelectorAll(".checkbox-form input[type='checkbox']")
        .forEach((checkbox) => {
            checkbox.addEventListener("change", updatePermissions);
        });

    function createNewRecord() {

        const password = document.getElementById("password")?.value;
        const confirm_password = document.getElementById("password2")?.value;
        const phone = document.getElementById("phone-no")?.value;
        const name = document.getElementById("cname-arabic")?.value;

        // if (!password || !confirm_password) {
        //     alert("الرجاء ادخال وتاكيد كلمة السر");
        //     return
        // }
        // if (!phone || !name) {
        //     alert("الرجاء ادخال اسم ورقم هاتف العميل");
        //     return
        // }

        // if (password != confirm_password) {
        //     alert(" !فشل تاكيد كلمة السر , ادخال مختلف ");
        //     return
        // }


        event.preventDefault();

        // Get selected country, skip if index is 0 (reset value)
        const currencySelect = document.getElementById("currency");
        const selectedCurrencyName =
            currencySelect.selectedIndex !== 0
                ? currencySelect.options[currencySelect.selectedIndex].text
                : "";

        // Get selected item-main, skip if index is 0 (reset value)
        const subSelect = document.getElementById("sub-category");
        const selectedSubText =
            subSelect.selectedIndex !== 0
                ? subSelect.options[subSelect.selectedIndex].text
                : "";

        // Get selected item-sub-main, skip if index is 0 (reset value)
        const installmentsSelect = document.getElementById("installments");
        const selectedInstallmentsText =
            installmentsSelect.selectedIndex !== 0
                ? installmentsSelect.options[installmentsSelect.selectedIndex]
                    .text
                : "";

        // Get selected company, skip if index is 0 (reset value)
        const typesSelect = document.getElementById("types");
        const selectedTypesText =
            typesSelect.selectedIndex !== 0
                ? typesSelect.options[typesSelect.selectedIndex].text
                : "";

        // Determine account_type based on the selected radio button
        const clientRadio = document.getElementById("client");
        const sourceRadio = document.getElementById("source");
        const accountType = clientRadio?.checked
            ? clientRadio.value
            : sourceRadio?.checked
                ? sourceRadio.value
                : "";

        // Get the client_stop checkbox value
        const clientStopCheckbox = document.getElementById("client-stop");
        const clientStopValue = clientStopCheckbox?.checked ? 1 : 0;

        // Get the cuurencyFlag checkbox value
        const cuurencyFlagCheckbox = document.getElementById("currency-flag");
        const cuurencyFlagValue = cuurencyFlagCheckbox?.checked ? 1 : 0;

        // Data object with correct CSRF token retrieval

        const data = {
            csrfmiddlewaretoken: getCSRFToken(),
            client_id: document.getElementById("cno")?.value || "",
            client_name: document.getElementById("cname-arabic")?.value || "",
            address: document.getElementById("address")?.value || "",
            email: document.getElementById("email")?.value || "",
            website: document.getElementById("website")?.value || "",
            phone: document.getElementById("phone-no")?.value || "",
            mobile: document.getElementById("mobile-no")?.value || "",
            last_transaction:
                document.getElementById("last-history")?.value || "",
            account_type: accountType,
            limit: document.getElementById("limit")?.value || "",
            limit_value: document.getElementById("limit-value")?.value || "",
            client_stop: clientStopValue,

            types: selectedTypesText,
            installments: selectedInstallmentsText,
            sub_category: selectedSubText,
            currency: selectedCurrencyName,
            other: document.getElementById("text-area")?.value || "",
            permissions: permissions,
            curr_flag: cuurencyFlagValue,
            password: document.getElementById("password")?.value || null,
        };
        console.log(data);

        customFetch("api/create-client", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(), // Add the CSRF token here
            },
            body: JSON.stringify(data),
        })
            .then((response) => {
                if (response.ok) {
                    alert("Record created successfully!");
                    refreshTable();
                } else {
                    response.text().then((errorMessage) => {
                        //alert("Error creating record.");
                        alert("Server error message:" + errorMessage);
                        //console.log("CSRF Token:", getCSRFToken()); // Check the value of the CSRF token
                    });
                }
            })
            .catch((error) => console.error("Error:", error));
    }
    document
        .getElementById("update-record-button")
        .addEventListener("click", function (event) {
            updateRecord();
        });
    function updateRecord() {
        // Get selected country, skip if index is 0 (reset value)
        const currencySelect = document.getElementById("currency");
        const selectedCurrencyName =
            currencySelect.selectedIndex !== 0
                ? currencySelect.options[currencySelect.selectedIndex].text
                : "";

        // Get selected item-main, skip if index is 0 (reset value)
        const subSelect = document.getElementById("sub-category");
        const selectedSubText =
            subSelect.selectedIndex !== 0
                ? subSelect.options[subSelect.selectedIndex].text
                : "";

        // Get selected item-sub-main, skip if index is 0 (reset value)
        const installmentsSelect = document.getElementById("installments");
        const selectedInstallmentsText =
            installmentsSelect.selectedIndex !== 0
                ? installmentsSelect.options[installmentsSelect.selectedIndex]
                    .text
                : "";

        // Get selected company, skip if index is 0 (reset value)
        const typesSelect = document.getElementById("types");
        const selectedTypesText =
            typesSelect.selectedIndex !== 0
                ? typesSelect.options[typesSelect.selectedIndex].text
                : "";

        // Determine account_type based on the selected radio button
        const clientRadio = document.getElementById("client");
        const sourceRadio = document.getElementById("source");
        const accountType = clientRadio?.checked
            ? clientRadio.value
            : sourceRadio?.checked
                ? sourceRadio.value
                : "";

        // Get the client_stop checkbox value
        const clientStopCheckbox = document.getElementById("client-stop");
        const clientStopValue = clientStopCheckbox?.checked ? 1 : 0;

        // Get the cuurencyFlag checkbox value
        const cuurencyFlagCheckbox = document.getElementById("currency-flag");
        const cuurencyFlagValue = cuurencyFlagCheckbox?.checked ? 1 : 0;

        // Data object with correct CSRF token retrieval

        const data = {
            csrfmiddlewaretoken: getCSRFToken(),
            client_id: document.getElementById("cno")?.value || "",
            client_name: document.getElementById("cname-arabic")?.value || "",
            address: document.getElementById("address")?.value || "",
            email: document.getElementById("email")?.value || "",
            website: document.getElementById("website")?.value || "",
            phone: document.getElementById("phone-no")?.value || "",
            mobile: document.getElementById("mobile-no")?.value || "",
            last_transaction:
                document.getElementById("last-history")?.value || "",
            account_type: accountType,
            limit: document.getElementById("limit")?.value || "",
            limit_value: document.getElementById("limit-value")?.value || "",
            client_stop: clientStopValue,

            types: selectedTypesText,
            installments: selectedInstallmentsText,
            sub_category: selectedSubText,
            currency: selectedCurrencyName,
            other: document.getElementById("text-area")?.value || "",
            permissions: permissions,
            curr_flag: cuurencyFlagValue,
        };
        console.log(data);
        customFetch("api/update-client", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(), // Add the CSRF token here
            },
            body: JSON.stringify(data),
        })
            .then((response) => {
                if (response.ok) {
                    alert("Record updated successfully!");
                    refreshTable();

                } else {
                    alert("Error updating record.");
                    console.log(getCSRFToken()); // Check the value of the CSRF token
                }
            })
            .catch((error) => console.error("Error:", error));
    }
    document
        .getElementById("deleteButton")
        .addEventListener("click", function (event) {
            deleteRecord();
        });
    function deleteRecord() {
        const confirmation = window.confirm(
            "هل أنت متأكد من أنك تريد حذف هذا السجل؟"
        );
        if (!confirmation) {
            return;
        }
        const data = {
            csrfmiddlewaretoken: getCSRFToken(),
            client_id: document.getElementById("cno")?.value || "",
        };

        customFetch("api/delete-client", {
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

    // Combined filter function
    function applyFilters(pageno = 1, pagesize = pageSize) {
        console.time("applyFiltersTime");
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
            id: getInputValue("cno"),
            name: getInputValue("cname-arabic"),
            email: getInputValue("email"),
            phone: getInputValue("phone-no"),
            mobile: getInputValue("mobile-no"),
            page: parseInt(pageno, 10) || 1,
            size: pagesize || 100,
        };

        console.log("Filter values:", filterValues);

        // Function to get CSRF token
        function getCSRFToken() {
            const csrfInput = document.querySelector(
                "[name=csrfmiddlewaretoken]"
            );
            return csrfInput ? csrfInput.value : "";
        }
        console.time("FilterTime");
        // Perform the fetch request
        customFetch("api/filter-all-clients", {
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
                console.time("tableTime");
                console.log("response: ", data);
                console.log("filter data", data.data);

                // Update Tabulator table
                if (pageno === 1) {
                    table.replaceData(data.data);
                    currentPage = 1;
                } else {
                    const scrollPosition = tableContainer.scrollTop;
                    table.addData(data.data);
                    tableContainer.scrollTop = scrollPosition;
                }

                lastPage = data.page_no === data.last_page;

                console.timeEnd("tableTime");

                console.time("PaginationTime");
                updatePagination(data.last_page, data.page_no);
                console.timeEnd("PaginationTime");
            })
            .catch((error) => {
                console.error("Error fetching filtered data:", error.message);
            })
            .finally(() => {
                console.timeEnd("FilterTime");
                console.timeEnd("applyFiltersTime");
                active_url = "server_filtered_data";
                isLoading = false;
                hideLoader();
            });
    }

    // Add event listeners to all filter inputs
    const filterInputs = [
        "cname-arabic",
        "cno",
        "email",
        "phone-no",
        "mobile-no",
    ];

    function debounce(func, wait) {
        let timeout;
        return function (...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    // Apply debounce to applyFilters with a 300ms delay
    const debouncedApplyFilters = debounce(() => applyFilters(1), 390);

    filterInputs.forEach((inputId) => {
        document
            .getElementById(inputId)
            .addEventListener("input", () => {
                debouncedApplyFilters();
            });
    });

    ///////////

    ///////////

    let currentPage = 1; // Tracks the current page
    let lastPage = false; // Indicates if the last page is reached
    let isLoading = false; // Prevents multiple fetch calls
    const pageSize = 100; // Number of rows per page
    const tableContainer = document.getElementById("users-table");// Table scroll container
    // Function to fetch and append the next page of data
    const fetchNextPage = () => {
        if (!lastPage) {
            currentPage++;
            console.log(`Fetching page ${currentPage}...`);
            console.log("fetching active url : ", active_url);

            if (active_url == "server_filtered_data") {
                //console.log("apply filters current page: ",currentPage);
                //applyFilters(currentPage, pageSize);
            } else {
                refreshTable({ page: currentPage, size: pageSize });
            }
            //hideLoader();
        }
    };

    // Scroll event listener
    const handleScroll = () => {
        //console.log("scroll area");
        const scrollPosition = tableContainer.scrollTop + tableContainer.clientHeight;
        const scrollThreshold = tableContainer.scrollHeight - 2000; // Adjust threshold as needed
        console.log("isLoading: ", isLoading);
        console.log("lastPage: ", lastPage);

        if (scrollPosition >= scrollThreshold && !lastPage && !isLoading) {
            console.log("scrollPosition: ", scrollPosition);
            console.log("scrollThreshold: ", scrollThreshold);
            console.log("scrollHeight: ", tableContainer.scrollHeight);
            //console.log("lastPage: ",lastPage);
            //console.log("isLoading: ",isLoading);
            isLoading = true;
            showLoader();
            fetchNextPage();
        }
    };

    // Attach the scroll event listener
    tableContainer.addEventListener("scroll", handleScroll);

    // Debounce function definition
    function debounce(func, wait) {
        let timeout;
        return function (...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    // Apply debounce to applyFilters with a 300ms delay
    //const debouncedApplyFilters = debounce(() => applyFilters(1), 390);
    refreshTable({ page: 1, size: 100 });

    function showLoader() {
        const loader = document.getElementById("loader-element");
        loader.classList.remove("d-none"); // Show the loader by removing d-none
        loader.classList.add("d-flex"); // Ensure d-flex is applied for flexbox display
        //console.log("loader shown");
    }

    function hideLoader() {
        const loader = document.getElementById("loader-element");

        // Set a delay (e.g., 2000ms = 2 seconds)
        setTimeout(function () {
            loader.classList.remove("d-flex"); // Remove d-flex
            loader.classList.add("d-none"); // Hide the loader by adding d-none
            //console.log("loader hidden after delay");
        }, 3000); // 2000ms = 2 seconds delay
    }
    function updatePagination(lastPage, currentPage) {
        const pagination = document.querySelector(".pagination");
        const existingPageLinks = pagination.querySelectorAll(".page-item:not(:first-child):not(:last-child):not(#page-size)");
        //console.log("existingPageLinks: ",existingPageLinks);

        const startPage = Math.max(1, currentPage);
        const endPage = Math.min(lastPage, startPage + 2);
        //console.log("startPage: ",startPage);
        //console.log("endPage: ",endPage);

        let index = 0; // Track the current index in existing page items
        for (let i = startPage; i <= endPage; i++) {
            let pageItem;
            if (index < existingPageLinks.length) {
                //console.log("if: done");
                // Update an existing item
                pageItem = existingPageLinks[index];
                pageItem.querySelector(".page-link").innerText = i;
                pageItem.querySelector(".page-link").setAttribute("data-page", i);
            } else {
                //console.log("else: done");
                // Add a new item if needed
                pageItem = document.createElement("li");
                pageItem.className = "page-item";
                pageItem.innerHTML = `<a class="page-link" href="#" data-page="${i}">${i}</a>`;
                pagination.insertBefore(pageItem, pagination.querySelector("li:last-child"));
            }
            pageItem.querySelector(".page-link").classList.toggle("page-link-active", i === currentPage); // Set active class
            index++;
            //console.log("index: ",index);
        }

        // Remove any extra items beyond the new range
        /*while (index < existingPageLinks.length) {
            pagination.removeChild(existingPageLinks[index]);
            index++;
        }*/

        // Update Previous button
        const previousBtn = document.querySelector(".page-prev");
        previousBtn.classList.toggle("item-disabled", currentPage === 1);
        previousBtn.querySelector(".page-link").setAttribute("data-page", currentPage - 1);
        //console.log("previousBtn: ",previousBtn);
        // Update Next button
        const nextBtn = document.querySelector(".page-next");
        nextBtn.classList.toggle("item-disabled", currentPage === endPage);
        nextBtn.querySelector(".page-link").setAttribute("data-page", currentPage + 1);
        //console.log("nextBtn: ",nextBtn);
        // Update First button
        const firstBtn = document.querySelector(".page-first");
        firstBtn.querySelector(".page-link").setAttribute("data-page", 1);
        //console.log("firstBtn: ",firstBtn);
        // Update Last button
        const lastBtn = document.querySelector(".page-last");
        lastBtn.querySelector(".page-link").setAttribute("data-page", lastPage);
        //console.log("lastBtn: ",lastBtn);
        //update no of pages paragraph
        document.getElementById("page-total").innerHTML = "تم تحميل " + currentPage + " من اجمالي " + lastPage + " صفحات ";
    }


    // Example usage with API response
    //const response = { last_page: 10, page_no: 3 }; // Example data
    //updatePagination(response.last_page, response.page_no);

    // Event listener for page links
    document.querySelector(".pagination").addEventListener("click", function (event) {
        const target = event.target;
        if (target.classList.contains("page-link") &&
            !target.parentNode.classList.contains("disabled") &&
            !target.closest("#page-size")) {  // Ensures page-size is not part of the event
            event.preventDefault();
            const selectedPage = parseInt(target.getAttribute("data-page"), 10);
            const selectedPageSize = document.getElementById("page-size").value;

            if (lastPage) {
                return
            }

            // Fetch data for selected page
            console.log(`Fetching data for page: ${selectedPage}, with page size ${selectedPageSize}, for ${active_url}`);
            if (active_url == "server_filtered_data") {
                currentPage = selectedPage;
                //applyFilters(selectedPage,selectedPageSize);
            } else {
                currentPage = selectedPage;
                refreshTable({ page: selectedPage, size: selectedPageSize });
            }
        }
    });


    // Event listener for page size change
    document.querySelector("#page-size").addEventListener("change", function () {
        const selectedPageSize = this.value;
        const selectedPage = document.querySelector(".page-link.page-link-active").innerHTML;

        //console.log(`Selected page size: ${selectedPageSize}`);
        console.log(`Fetching data for page: ${selectedPage}, with page size ${selectedPageSize}, for ${active_url}`);
        if (active_url == "server_filtered_data") {
            // applyFilters(selectedPage,selectedPageSize);
        } else {
            refreshTable({ page: selectedPage, size: selectedPageSize });
        }
    });
    ///////////////////
});

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
                title: "رقم المورد",
                field: "clientid",
                sorter: "number",
                visible: true,
                width: 100,
            },
            {
                title: "اسم المورد",
                field: "name",
                sorter: "string",
                visible: true,
                width: 150,
            },
            {
                title: "الرصيد",
                field: "balance",
                sorter: "string",
                visible: true,
                width: 100,
            },

            {
                title: "السقف",
                field: "loan_limit",
                sorter: "number",
                visible: true,
                width: 100,
            },
            {
                title: "الحالة",
                field: "category",
                sorter: "string",
                visible: true,
                width: 100,
            },
            {
                title: "اخر دفعة",
                field: "last_transaction",
                sorter: "string",
                visible: false,
                width: 100,
            },
            {
                title: "قيمة الدفعة",
                field: "last_transaction_amount",
                sorter: "string",
                visible: false,
                width: 100,
            },
            {
                title: "اجمالي الدفعات",
                field: "paid_total",
                sorter: "string",
                visible: false,
                width: 100,
            },
        ],
        placeholder: "No Data Available",
        rowFormatter: function (row) {
            var rowData = row.getData(); // Get the row data

            // You can add more conditions as needed
        }, // Message when no data is present or after filtering
        tableBuilt: function () {
            console.log("table built");
        },
    });

    refreshTable();

    function refreshTable({ page = 1, size = 100 } = {}) {
        console.time("fetchData"); // Start timer
        customFetch(`/api/sources-api/?page=${page}&size=${size}`, {
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
    table.on("rowClick", function (e, row) {
        console.log("Row clicked after data update:", row.getData());
        const id = row.getData().clientid; // Get pno of the clicked row
        const rowData = row.getData();
        const url = "/account-statements";
        const fullUrl = `${url}?supplier=${id}`;
        openWindow(fullUrl);
        //populateInputFields(rowData);
        console.log("Clicked id:", id);
    });
    function populateInputFields(data) {
        // For 'countries' dropdown (set selected item based on 'data.itemsize')
        const currencySelect = document.getElementById("currency");
        const currencyOptions = currencySelect.options;
        let currencySelected = false; // Flag to track if a match is found
        for (let i = 0; i < currencyOptions.length; i++) {
            if (currencyOptions[i].text === data.accountcurr) {
                // Compare text (country name)
                currencySelect.selectedIndex = i; // Set the selected option
                currencySelected = true; // Mark as selected
                break;
            }
        }
        if (!currencySelected) {
            // Reset if no match found
            currencySelect.selectedIndex = 0; // Set the selected option to the first one
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
        .addEventListener("click", function () {
            clearForm();
        });
    function clearForm() {
        // Select all inputs except the CSRF token
        const inputs = document.querySelectorAll(
            "input:not([name='csrfmiddlewaretoken']), select"
        );
        inputs.forEach((input) => {
            if (input.type === "radio" || input.type === "checkbox") {
                input.checked = false; // Uncheck radios/checkboxes
            } else {
                input.value = ""; // Clear text, number, etc.
            }
        });

        // Optionally reset dropdowns
        const selects = document.querySelectorAll("select");
        selects.forEach((select) => {
            if (select.id !== "page-size") {
                select.selectedIndex = 0; // Reset to first option
            }
        });

        refreshTable();
    }


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
        function getSelectedRadioValue(name) {
            const selectedRadio = document.querySelector(
                `input[name="${name}"]:checked`
            );
            return selectedRadio ? selectedRadio.id : null;
        }

        // Capture filter values dynamically
        const filterValues = {
            id: getInputValue("cno"),
            name: getInputValue("cname-arabic"),
            email: getInputValue("email"),
            phone: getInputValue("phone-no"),
            mobile: getInputValue("mobile-no"),
            fromdate: getInputValue("from-date"),
            todate: getInputValue("to-date"),
            subtype: getSelectedText("sub-type"),
            filter: getSelectedRadioValue("filter"), // Radio buttons
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
        customFetch("/api/filter-all-sources", {
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
                    table.setData(data.data);
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
        "from-date",
        "to-date",
        "sub-type",
        "all",
        "paid",
        "deptor",
        "creditor",
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

    function dateFilter() {
        customFetch("/api/filter-all-clients", {
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

    ////full report
    // Function to toggle column visibility based on checkbox
    document
        .getElementById("detailed-check")
        .addEventListener("change", function () {
            const isChecked = this.checked;

            // Show or hide columns based on checkbox state
            if (isChecked) {
                table.showColumn("last_transaction"); // Show/hide Column 3
                table.showColumn("last_transaction_amount");
                table.showColumn("paid_total");
            } else {
                table.hideColumn("last_transaction"); // Show/hide Column 3
                table.hideColumn("last_transaction_amount");
                table.hideColumn("paid_total");
            }
        });

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
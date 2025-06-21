document.addEventListener("DOMContentLoaded", function () {

    const show_sell_price_permission = document.getElementById("show_sell_price_sellinvoice_perm").value;
    console.log("show_sell_price_permission: ", show_sell_price_permission);
    const toggler = document.getElementById('more-info-toggler');
    const moreInfo = document.getElementById('more-info');



    toggler.addEventListener('click', () => {
        moreInfo.classList.toggle('show');

        // Toggle icon class
        if (moreInfo.classList.contains('show')) {
            toggler.classList.remove('bi-arrow-down-circle');
            toggler.classList.add('bi-arrow-up-circle');
        } else {
            toggler.classList.remove('bi-arrow-up-circle');
            toggler.classList.add('bi-arrow-down-circle');
        }
    });

    /////////
    const products_table = new Tabulator("#products-table", {
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
        data: [],//contextData.data, // Placeholder, will be loaded dynamically
        columns: [],
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

    const invoices_table = new Tabulator("#invoices-table", {
        index: "invoice_no", // Use "fileid" as the unique row identifier
        height: "auto", // Adjust height or set a fixed height
        layout: "fitColumns",
        selectable: true,
        columnHeaderVertAlign: "bottom",
        data: [],//contextData.data, // Placeholder, will be loaded dynamically
        columns: [
            { title: "رقم الفاتورة", field: "invoice_no", headerSort: false },
            {
                title: "تاريخ الفاتورة",
                field: "date_time", width: 160,
            },
            { title: "العميل", field: "client_name", width: 90 },
            { title: "حالة الدفع", field: "payment_status" },
            { title: "المبلغ الإجمالي", field: "amount", sorter: "number", formatter: "money", formatterParams: { thousand: ",", symbol: " دل ", symbolAfter: "p" } },
            { title: "الخصم", field: "discount", sorter: "number", formatter: "money", formatterParams: { thousand: ",", symbol: " دل ", symbolAfter: "p" } },
            { title: "الضرائب", field: "taxes", sorter: "number", formatter: "money", formatterParams: { thousand: ",", symbol: " دل ", symbolAfter: "p" } },
            { title: "صافي الفاتورة", field: "net_amount", sorter: "number", formatter: "money", formatterParams: { thousand: ",", symbol: " دل ", symbolAfter: "p" } },
            { title: "ترجيع", field: "returned", sorter: "number", formatter: "money", formatterParams: { thousand: ",", symbol: " دل ", symbolAfter: "p" } },
            { title: "المدفوع", field: "paid_amount", sorter: "number", formatter: "money", formatterParams: { thousand: ",", symbol: " دل ", symbolAfter: "p" } },
            { title: "الموظف", field: "employee" },
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
        const csrfInput = document.querySelector(
            "[name=csrfmiddlewaretoken]"
        );
        return csrfInput ? csrfInput.value : "";
    }
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
    invoices_table.on("rowClick", function (e, row) {
        const hasInvoiceItemsPermission = document.getElementById("show_items_sellinvoice_perm").value;

        if (!hasInvoiceItemsPermission) {
            alert("لا تملك صلاحية عرض تفاصيل الفاتورة");
            return;
        }
        console.log("Row clicked:", row.getData().autoid);

        const id = row.getData().invoice_no;

        openWindow('/sell-invoice-profile/' + id + '/', 900);
        console.log("sent id: ", id);

    });

    let currentInvoicesPage = 1; // Tracks the current page
    let lastInvoicesPage = false; // Indicates if the last page is reached
    let isLoading = false; // Prevents multiple fetch calls
    const pageSize = 100; // Number of rows per page
    const invoicesTableContainer = document.getElementById("invoices-table");// Table scroll container
    // Function to fetch and append the next page of data
    const fetchNextPageForInvoices = () => {
        if (!lastInvoicesPage) {
            currentInvoicesPage++;
            console.log(`Fetching page ${currentInvoicesPage}...`);
            console.log("fetching active url : ", active_url);

            if (active_url == "server_filtered_data") {
                //console.log("apply filters current page: ",currentInvoicesPage);
                applyFiltersForInvoices(currentInvoicesPage, pageSize);
            } else {
                fetchInvoicesFromServer({ page: currentInvoicesPage, size: pageSize });
            }
            //hideInvoicesLoader();
            //scrollToLastRow();
        }
    };

    // Scroll event listener
    const handleScrollForInvoices = () => {
        //console.log("scroll area");
        const scrollPosition = invoicesTableContainer.scrollTop + invoicesTableContainer.clientHeight;
        const scrollThreshold = invoicesTableContainer.scrollHeight - 2000; // Adjust threshold as needed
        console.log("isLoading: ", isLoading);
        console.log("lastInvoicesPage: ", lastInvoicesPage);

        if (scrollPosition >= scrollThreshold && !lastInvoicesPage && !isLoading) {
            console.log("scrollPosition: ", scrollPosition);
            console.log("scrollThreshold: ", scrollThreshold);
            console.log("scrollHeight: ", invoicesTableContainer.scrollHeight);
            //console.log("lastInvoicesPage: ",lastInvoicesPage);
            //console.log("isLoading: ",isLoading);
            isLoading = true;
            showInvoicesLoader();
            fetchNextPageForInvoices();
        }
    };
    function updateInput(id, value) {
        document.getElementById(id).value = value;
    }
    function fetchInvoicesFromServer({ page = 1, size = 100 }) {
        //if (isLoading) return; // Prevent fetch if already loading
        //isLoading = true; // Set loading flag before initiating fetch

        // Use the URL in your fetch request


        console.time("fetchData"); // Start timer

        customFetch(`fetch-sellinvoices?page=${page}&size=${size}`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        })
            .then((response) => response.json())
            .then((data) => {
                console.log("Fetched Data:", data);
                active_url = "server_Data_No_Filter";
                console.log("active_url for pagination:", active_url);
                //console.log("page:", page);

                console.time("tableTime");
                //console.log("sort status: ", invoices_table.getDataCount());
                if (page === 1) {
                    // For the first page, replace the existing data
                    invoices_table.setData(data.data);
                    console.log("data set to the table");
                    //console.log("getDataCount: ", invoices_table.getDataCount());
                    currentInvoicesPage = 1;
                } else {
                    let scrollPosition = invoicesTableContainer.scrollTop; // Save scroll position
                    //let currentData = invoices_table.getData();  // Get current table data
                    //let combinedData = currentData.concat(data.data);  // Combine existing data with new data
                    invoices_table.addData(data.data);
                    invoicesTableContainer.scrollTop = scrollPosition;
                    console.log("data added to the table");
                    //console.log("getDataCount: ", invoices_table.getDataCount());
                }
                console.timeEnd("tableTime");

                // Update lastInvoicesPage flag
                lastInvoicesPage = data.page_no == data.last_page ? true : false;
                console.time("PaginationTime");
                updateInvoicesPagination(data.last_page, data.page_no);
                console.timeEnd("PaginationTime");
                updateInput("total", data.total_amount + " دل ");
                updateInput("cash", data.cash_amount + " دل ");
                updateInput("loan", data.loan_amount + " دل ");
                updateInput("returned", data.total_returned + " دل ");
                updateInput("discount", data.total_discount + " دل ");
                updateCalc();


                return data; // Return data for further processing
            })
            .catch((error) => console.error("Error fetching data:", error)).finally(() => {
                console.timeEnd("fetchData"); // End the timer regardless of success or failure
                isLoading = false; // Reset loading flag after fetch completes
                hideInvoicesLoader();
                scrollToLastRow();
            });
    }
    // Attach the scroll event listener
    invoicesTableContainer.addEventListener("scroll", handleScrollForInvoices);

    // Debounce function definition
    function debounce(func, wait) {
        let timeout;
        return function (...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    // Apply debounce to applyFilters with a 300ms delay
    //const debouncedApplyFiltersForInvoices = debounce(() => applyFiltersForInvoices(1), 390);
    applyFiltersForInvoices();

    function showInvoicesLoader() {
        const loader = document.getElementById("invoices-loader-element");
        loader.classList.remove("d-none"); // Show the loader by removing d-none
        loader.classList.add("d-flex"); // Ensure d-flex is applied for flexbox display
        //console.log("loader shown");
    }

    function hideInvoicesLoader() {
        const loader = document.getElementById("invoices-loader-element");

        // Set a delay (e.g., 2000ms = 2 seconds)
        setTimeout(function () {
            loader.classList.remove("d-flex"); // Remove d-flex
            loader.classList.add("d-none"); // Hide the loader by adding d-none
            //console.log("loader hidden after delay");
        }, 3000); // 2000ms = 2 seconds delay
    }
    function updateInvoicesPagination(lastInvoicesPage, currentInvoicesPage) {
        const pagination = document.querySelector(".invoices-pagination");
        const existingPageLinks = pagination.querySelectorAll(".invoices-page-item:not(:first-child):not(:last-child):not(#invoices-page-size)");
        //console.log("existingPageLinks: ",existingPageLinks);

        const startPage = Math.max(1, currentInvoicesPage);
        const endPage = Math.min(lastInvoicesPage, startPage + 2);
        //console.log("startPage: ",startPage);
        //console.log("endPage: ",endPage);

        let index = 0; // Track the current index in existing page items
        for (let i = startPage; i <= endPage; i++) {
            let pageItem;
            if (index < existingPageLinks.length) {
                //console.log("if: done");
                // Update an existing item
                pageItem = existingPageLinks[index];
                pageItem.querySelector(".invoices-page-link").innerText = i;
                pageItem.querySelector(".invoices-page-link").setAttribute("data-page", i);
            } else {
                //console.log("else: done");
                // Add a new item if needed
                pageItem = document.createElement("li");
                pageItem.className = "invoices-page-item";
                pageItem.innerHTML = `<a class="invoices-page-link" href="#" data-page="${i}">${i}</a>`;
                pagination.insertBefore(pageItem, pagination.querySelector("li:last-child"));
            }
            pageItem.querySelector(".invoices-page-link").classList.toggle("page-link-active", i === currentInvoicesPage); // Set active class
            index++;
            //console.log("index: ",index);
        }

        // Remove any extra items beyond the new range
        /*while (index < existingPageLinks.length) {
            pagination.removeChild(existingPageLinks[index]);
            index++;
        }*/

        // Update Previous button
        const previousBtn = document.querySelector(".invoices-page-prev");
        previousBtn.classList.toggle("item-disabled", currentInvoicesPage === 1);
        previousBtn.querySelector(".invoices-page-link").setAttribute("data-page", currentInvoicesPage - 1);
        //console.log("previousBtn: ",previousBtn);
        // Update Next button
        const nextBtn = document.querySelector(".invoices-page-next");
        nextBtn.classList.toggle("item-disabled", currentInvoicesPage === endPage);
        nextBtn.querySelector(".invoices-page-link").setAttribute("data-page", currentInvoicesPage + 1);
        //console.log("nextBtn: ",nextBtn);
        // Update First button
        const firstBtn = document.querySelector(".invoices-page-first");
        firstBtn.querySelector(".invoices-page-link").setAttribute("data-page", 1);
        //console.log("firstBtn: ",firstBtn);
        // Update Last button
        const lastBtn = document.querySelector(".invoices-page-last");
        lastBtn.querySelector(".invoices-page-link").setAttribute("data-page", lastInvoicesPage);
        //console.log("lastBtn: ",lastBtn);
        //update no of pages paragraph
        document.getElementById("invoices-page-total").innerHTML = "تم تحميل " + currentInvoicesPage + " من اجمالي " + lastInvoicesPage + " صفحات ";
    }


    // Example usage with API response
    //const response = { last_page: 10, page_no: 3 }; // Example data
    //updateInvoicesPagination(response.last_page, response.page_no);

    // Event listener for page links
    document.querySelector(".invoices-pagination").addEventListener("click", function (event) {
        const target = event.target;
        if (target.classList.contains("invoices-page-link") &&
            !target.parentNode.classList.contains("disabled") &&
            !target.closest("#page-size")) {  // Ensures page-size is not part of the event
            event.preventDefault();
            const selectedPage = parseInt(target.getAttribute("data-page"), 10);
            const selectedPageSize = document.getElementById("page-size").value;

            if (lastInvoicesPage) {
                return
            }

            // Fetch data for selected page
            console.log(`Fetching data for page: ${selectedPage}, with page size ${selectedPageSize}, for ${active_url}`);
            if (active_url == "server_filtered_data") {
                currentInvoicesPage = selectedPage;
                applyFiltersForInvoices(selectedPage, selectedPageSize);
            } else {
                currentInvoicesPage = selectedPage;
                fetchInvoicesFromServer({ page: selectedPage, size: selectedPageSize });
            }
        }
    });


    // Event listener for page size change
    document.querySelector("#invoices-page-size").addEventListener("change", function () {
        const selectedPageSize = this.value;
        const selectedPage = document.querySelector(".invoices-page-link.page-link-active").innerHTML;

        //console.log(`Selected page size: ${selectedPageSize}`);
        console.log(`Fetching data for page: ${selectedPage}, with page size ${selectedPageSize}, for ${active_url}`);
        if (active_url == "server_filtered_data") {
            applyFiltersForInvoices(selectedPage, selectedPageSize);
        } else {
            fetchInvoicesFromServer({ page: selectedPage, size: selectedPageSize });
        }
    });
    function scrollToLastRow() {
        invoices_table.setPage(invoices_table.getPageMax()).then(() => {
            setTimeout(() => {
                // Scroll to last row
                var lastRow = invoices_table.getRows().pop();
                if (lastRow) {
                    invoices_table.scrollToRow(lastRow, "bottom").catch(err => console.warn("Scroll Error:", err));
                }

                // Scroll the table container to the bottom
                let tableContainer = document.getElementById("users-table");
                if (tableContainer) {
                    tableContainer.scrollTop = tableContainer.scrollHeight;
                }
            }, 300); // Small delay to ensure content loads before scrolling
        });
    }

    function applyFiltersForInvoices(pageno = 1, pagesize = pageSize) {
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
            const checkedRadio = document.querySelector(`input[name="${name}"]:checked`);
            return checkedRadio ? checkedRadio.value : null;
        }

        // Capture filter values dynamically
        const filterValues = {
            client: getSelectedText("client"),
            fromdate: getInputValue("from-date"),
            todate: getInputValue("to-date"),
            invoice_no: getInputValue("autoid"),
            for_who: getInputValue("for-who"),
            client_rate: getSelectedText("client-category"),
            page: parseInt(pageno, 10) || 1,
            size: pagesize || 20,
        };

        const payment_status = getSelectedRadioValue("payment-status");  // Assuming 'cash' and 'loan' have the same name
        if (payment_status) filterValues.payment_status = payment_status;


        const price_status = getSelectedRadioValue("price-status");  // Assuming 'paid_status' and 'not_paid_status' have the same name
        if (price_status) filterValues.price_status = price_status;

        console.log("Filter values:", filterValues);

        // Function to get CSRF token
        function getCSRFToken() {
            const csrfInput = document.querySelector(
                "[name=csrfmiddlewaretoken]"
            );
            return csrfInput ? csrfInput.value : "";
        }

        console.time("FilterTime");

        customFetch("filter-sellinvoices", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify(filterValues),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`Network error: ${response.status} ${response.statusText}`);
                }
                return response.json();
            })
            .then((data) => {
                console.time("tableTime");
                console.log("response: ", data);
                console.log("filter data", data.data);

                // Update Tabulator table
                if (pageno === 1) {
                    invoices_table.replaceData(data.data);
                    currentInvoicesPage = 1;
                } else {
                    const scrollPosition = invoicesTableContainer.scrollTop;
                    invoices_table.addData(data.data);
                    invoicesTableContainer.scrollTop = scrollPosition;
                }

                lastInvoicesPage = data.page_no === data.last_page;

                console.timeEnd("tableTime");

                console.time("PaginationTime");
                updateInvoicesPagination(data.last_page, data.page_no);
                console.timeEnd("PaginationTime");
                updateInput("total", data.total_amount + " دل ");
                updateInput("cash", data.cash_amount + " دل ");
                updateInput("loan", data.loan_amount + " دل ");
                updateInput("returned", data.total_returned + " دل ");
                updateInput("discount", data.total_discount + " دل ");
                updateCalc();

            })
            .catch((error) => {
                console.error("Error fetching filtered data:", error.message);
            })
            .finally(() => {
                console.timeEnd("FilterTime");
                console.timeEnd("applyFiltersTime");
                active_url = "server_filtered_data";
                isLoading = false;
                hideInvoicesLoader();
                scrollToLastRow();
            });
    }
    function CustomApplyFiltersForInvoices(pageno = 1, pagesize = pageSize) {
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
            const checkedRadio = document.querySelector(`input[name="${name}"]:checked`);
            return checkedRadio ? checkedRadio.value : null;
        }

        // Capture filter values dynamically
        const filterValues = {
            client: getSelectedText("client"),
            //fromdate: getInputValue("from-date"),
            //todate: getInputValue("to-date"),
            invoice_no: getInputValue("autoid"),
            for_who: getInputValue("for-who"),
            client_rate: getSelectedText("client-category"),
            page: parseInt(pageno, 10) || 1,
            size: pagesize || 20,
        };

        const payment_status = getSelectedRadioValue("payment-status");  // Assuming 'cash' and 'loan' have the same name
        if (payment_status) filterValues.payment_status = payment_status;


        const price_status = getSelectedRadioValue("price-status");  // Assuming 'paid_status' and 'not_paid_status' have the same name
        if (price_status) filterValues.price_status = price_status;

        console.log("Filter values:", filterValues);

        // Function to get CSRF token
        function getCSRFToken() {
            const csrfInput = document.querySelector(
                "[name=csrfmiddlewaretoken]"
            );
            return csrfInput ? csrfInput.value : "";
        }

        console.time("FilterTime");

        customFetch("filter-sellinvoices", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify(filterValues),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`Network error: ${response.status} ${response.statusText}`);
                }
                return response.json();
            })
            .then((data) => {
                console.time("tableTime");
                console.log("response: ", data);
                console.log("filter data", data.data);

                // Update Tabulator table
                if (pageno === 1) {
                    invoices_table.replaceData(data.data);
                    currentInvoicesPage = 1;
                } else {
                    const scrollPosition = invoicesTableContainer.scrollTop;
                    invoices_table.addData(data.data);
                    invoicesTableContainer.scrollTop = scrollPosition;
                }

                lastInvoicesPage = data.page_no === data.last_page;

                console.timeEnd("tableTime");

                console.time("PaginationTime");
                updateInvoicesPagination(data.last_page, data.page_no);
                console.timeEnd("PaginationTime");
                updateInput("total", data.total_amount + " دل ");
                updateInput("cash", data.cash_amount + " دل ");
                updateInput("loan", data.loan_amount + " دل ");
                updateInput("returned", data.total_returned + " دل ");
                updateInput("discount", data.total_discount + " دل ");
                updateCalc();

            })
            .catch((error) => {
                console.error("Error fetching filtered data:", error.message);
            })
            .finally(() => {
                console.timeEnd("FilterTime");
                console.timeEnd("applyFiltersTime");
                active_url = "server_filtered_data";
                isLoading = false;
                hideInvoicesLoader();
                scrollToLastRow();
            });
    }
    document.getElementById("autoid").addEventListener("input", () => {
        CustomApplyFiltersForInvoices();
    });

    // Add event listeners to all filter inputs
    const filterInputsForInvoices = [
        //"autoid",
        "client",
        "from-date",
        "to-date",
        "for-who",
        "client-category",
        "loan-radio",
        "cash-radio",
        "not_paid_status",
        "paid_status",
        "price_status_all",
        "payment_status_all",
    ];

    function debounce(func, wait) {
        let timeout;
        return function (...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    // Apply debounce to applyFilters with a 300ms delay
    const debouncedApplyFiltersForInvoices = debounce(() => applyFiltersForInvoices(1, pageSize), 390);
    filterInputsForInvoices.forEach((inputId) => {
        document
            .getElementById(inputId)
            .addEventListener("input", () => {
                debouncedApplyFiltersForInvoices();
            });
    });

    const element = document.getElementById("client");
    const choices = new Choices(element, {
        searchEnabled: true,
        removeItemButton: true, // Optional: allows removal of selected items
        //addItems: true, // Allows adding items
        //addChoices: true,
        duplicateItemsAllowed: false,
    });
    element.addEventListener('choice', function (event) {
        debouncedApplyFiltersForInvoices();
    });
    ///////////////////

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
                    const tagName = element.tagName.toLowerCase();
                    const type = element.type;

                    if (tagName === "input" || tagName === "textarea") {
                        if (type === "radio" || type === "checkbox") {
                            element.checked = false; // Reset checkboxes and radio buttons
                        } else {
                            element.value = ""; // Reset text inputs and textareas
                        }
                    } else if (tagName === "select") {
                        element.selectedIndex = 0; // Reset select dropdowns
                    }
                }
            });

            if (invoices_table) {
                invoices_table.clearFilter(); // Clear all filters applied
                fetchInvoicesFromServer({ page: 1, size: 100 });
            }
        });
    }

    function updateCalc() {

    }
    document.getElementById("export-btn-excel").addEventListener("click", exportToExcel);
    document.getElementById("export-btn-pdf").addEventListener("click", exportToPDF);
    function exportToExcel() {
        invoices_table.download("xlsx", "table_data.xlsx"); // 'xlsx' is the file format
    }

    // Example of vfs_fonts.js

    function exportToPDF() {
        // Get visible column field names
        let visibleColumns = invoices_table
            .getColumns() // Retrieve column components
            .filter((col) => col.isVisible()) // Check if the column is visible
            .map((col) => col.getField()); // Get the field names of visible columns

        // Filter table data based on visible columns
        let tableData = invoices_table.getData().map((row) => {
            // Create a new object with only visible fields
            return visibleColumns.reduce((filteredRow, field) => {
                filteredRow[field] = row[field]; // Copy value of visible field
                return filteredRow;
            }, {});
        });

        // Now `filteredData` contains only the visible columns from tableData
        //console.log(tableData);

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
    //////

    const modal = document.getElementById('exampleModal');
    const openModalBtn = document.querySelector('[data-bs-toggle="modal"][data-bs-target="#exampleModal"]'); // Button that opens modal

    // Ensure the modal is focusable and no `aria-hidden` is blocking when shown
    modal.addEventListener('shown.bs.modal', function () {
        const firstFocusable = modal.querySelector('button, input, a, select, textarea'); // First focusable element inside the modal

        // Remove aria-hidden and inert when the modal is shown
        modal.removeAttribute('aria-hidden');
        modal.removeAttribute('inert');

        // Set focus to the first element inside the modal
        if (firstFocusable) {
            firstFocusable.focus();
        }
    });

    // Ensure aria-hidden and inert is applied when modal is hidden
    modal.addEventListener('hidden.bs.modal', function () {
        // Add inert and aria-hidden attributes when the modal is closed
        modal.setAttribute('aria-hidden', 'true');
        modal.setAttribute('inert', ''); // Prevent interaction with the modal

        if (openModalBtn) {
            // Return focus to the button that opened the modal
            openModalBtn.focus();
        }

        // Ensure body scroll is restored when modal closes
        document.body.style.overflow = '';
    });

    // Fix body overflow issue (for modals causing scroll issues)
    openModalBtn.addEventListener('click', function () {
        // Prevent body from scrolling when modal is opened
        document.body.style.overflow = 'hidden';
    });

    document.getElementById("print-btn").addEventListener("click", () => {
        const data = {
            label: "today_sell_invoice",
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

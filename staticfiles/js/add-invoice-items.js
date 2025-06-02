document.addEventListener("DOMContentLoaded", function () {
    const rawData = document.getElementById("context-data").textContent;
    const contextData = JSON.parse(rawData);
    console.log(contextData);
    // Fetch client ID from the URL query string
    const id = contextData.invoice; // Retrieve the client ID from the URL (e.g., ?id=123)
    const source = contextData.source;
    const date = contextData.date;
    const rate = contextData.rate;
    const temp = contextData.temp;
    const currency = contextData.currency;

    // document.getElementById("date").value = date;
    document.getElementById("source-name").value = source;
    //document.getElementById("invoice-autoid").value = id;

    document.getElementById("currency").value = currency
        .match(/\((.*?)\)/)[1]
        .trim();
    if (temp == 1) {
        document.getElementById("temp").checked = true;
    } else {
        document.getElementById("temp").checked = false;
    }

    // Initialize Tabulator table
    const table = new Tabulator("#users-table", {
        index: "fileid", // Use "fileid" as the unique row identifier
        height: "auto", // Adjust height or set a fixed height
        layout: "fitColumns",
        selectable: true,
        columnHeaderVertAlign: "bottom",
        data: [], // Placeholder, will be loaded dynamically
        columns: [
            { title: "رقم خاص", field: "pno", width: 90 },
            { title: "الرقم الاصلي", field: "itemno", width: 90 },
            { title: "اسم الشركة", field: "companyproduct", width: 90 },
            { title: "رقم الشركة", field: "replaceno", width: 90 },
            { title: "اسم الصنف", field: "itemname", width: 190 },
            { title: "الكمية", field: "itemvalue", width: 90 },
            { title: "سعر البيع", field: "buyprice", width: 90 },
            { title: "مكان التخزين", field: "itemplace", width: 90 },
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


    // Attach a rowClick event to select the row for deletion
    table.on("rowClick", function (e, row) {
        if (row.getData().itemvalue > 0) {
            if (
                confirm("يوجد رصيد لهذا الصنف مسبقا \n هل تريد الاستمرار") == true
            ) {
                populateInputFields(row.getData());
                // Store the values in sessionStorage
                sessionStorage.setItem("prev_quantity", row.getData().itemvalue);
                sessionStorage.setItem("prev_cost_price", row.getData().costprice);
                sessionStorage.setItem("prev_buy_price", row.getData().buyprice);
                sessionStorage.setItem("prev_less_price", row.getData().lessprice);
            } else {
                return;
            }
        } else {
            populateInputFields(row.getData());
        }

        //window.currentRow = row; // Save the selected row for later use
        //second_table.addRow(row.getData()); // Add the row data to second_table
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
    document
        .getElementById("clear-btn")
        .addEventListener("click", function () {
            clearForm();
        });
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
                        element.value = ""; // Reset input and textarea values
                    } else if (element.tagName.toLowerCase() === "select") {
                        element.selectedIndex = 0; // Reset select dropdowns
                    }
                }
            });

            // Clear any filters applied in the table (Tabulator's clearFilter method)
            // Clear any applied filters in Tabulator
            if (table) {
                table.clearFilter(); // Clear all filters applied in the Tabulator instance
            }
        });
    }
    document.getElementById("add-btn").addEventListener("click", function () {
        const rate = contextData.rate;
        const date = contextData.date;

        const res = document.getElementById("res-value").value || "";
        const temp = document.getElementById("temp-value").value || "";
        const buy =
            parseFloat(document.getElementById("org-price").value) *
            parseFloat(rate) || "";
        const sell = document.getElementById("sell-price").value || "";
        const less = document.getElementById("less-price").value || "";
        const org = document.getElementById("org-price").value || "";
        const quantity = document.getElementById("item-value").value || "";
        const currency = document.getElementById("currency").value || "";
        const source = document.getElementById("source-name").value || "";
        const place = document.getElementById("place").value || "";
        const invoice = document.getElementById("invoice").value || "";

        const itemname = document.getElementById("item-name").value || 0;
        const orgno = document.getElementById("org-no").value || 0;
        const pno = document.getElementById("pno").value || "";
        const company = document.getElementById("company-name").value || "";
        const companyno = document.getElementById("company-no").value || "";
        const main_cat = document.getElementById("main-cat").value || "";

        // Store the values in sessionStorage
        const prev_quantity = sessionStorage.getItem("prev_quantity") || 0;
        const prev_cost_price = sessionStorage.getItem("prev_cost_price") || 0;
        const prev_buy_price = sessionStorage.getItem("prev_buy_price") || 0;
        const prev_less_price = sessionStorage.getItem("prev_less_price") || 0;

        console.log(prev_quantity);

        const data = {
            resvalue: res,
            itemvalueb: temp,
            orderprice: buy,
            buyprice: sell,
            lessprice: less,
            orgprice: org,
            itemvalue: quantity,
            currency: currency,
            source: source,
            invoice_id: invoice,
            itemplace: place,
            main_cat: main_cat,
            itemname: itemname,
            itemno: orgno,
            pno: pno,
            companyproduct: company,
            replaceno: companyno,
            rate: rate,
            date: date,
            prev_quantity: prev_quantity,
            prev_cost_price: prev_cost_price,
            prev_buy_price: prev_buy_price,
            prev_less_price: prev_less_price,
            isTemp: contextData.temp,
        };
        console.log("data sent: ", data);
        const baseUrl = window.location.origin;

        customFetch(`${baseUrl}/api/create-invoice-item/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        })
            .then((response) => response.json())
            .then((result) => {
                console.log(result);
                const invoiceId = document.getElementById("invoice").value.trim(); // Replace with the actual invoice ID
                fetchInvoiceItems(invoiceId).then((items) => {
                    if (items) {
                        console.log("Invoice items:", items);
                        second_table.replaceData(items); // Add the row data to second_table
                        // Handle the fetched items, e.g., display them in the UI
                    } else {
                        console.log("No items fetched or an error occurred.");
                    }
                });
                clearForm();
            })
            .catch((error) => {
                console.error("Error:", error);
            });
    });
    const second_table = new Tabulator("#new-table", {
        index: "fileid", // Use "fileid" as the unique row identifier
        height: "auto", // Adjust height or set a fixed height
        layout: "fitColumns",
        selectable: true,
        columnHeaderVertAlign: "bottom",
        data: [], // Placeholder, will be loaded dynamically
        columns: [
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

    const invoiceId = contextData.invoice;// Replace with the actual invoice ID
    console.log("initial invoice ", invoiceId);
    fetchInvoiceItems(invoiceId).then((items) => {
        if (items) {
            console.log("Invoice items at page load:", items);
            second_table.replaceData(items); // Add the row data to second_table
            // Handle the fetched items, e.g., display them in the UI
        } else {
            console.log("No items fetched or an error occurred.");
        }
    });
    //show model select items for selected maintype
    // Get the select elements
    const modelSelect = document.getElementById("model");
    const mainTypeSelect = document.getElementById("item-main");

    // Event listener for mainType select change
    mainTypeSelect.addEventListener("change", function () {
        const selectedMainType = mainTypeSelect.value;

        // Loop through all model options and hide those that don't match the selected maintype
        Array.from(modelSelect.options).forEach((option) => {
            const modelMainType = option.getAttribute("data-main-type");

            if (selectedMainType === "" || modelMainType === selectedMainType) {
                option.style.display = "block"; // Show option if it matches
            } else {
                option.style.display = "none"; // Hide option if it doesn't match
            }
        });

        // Optionally, clear the model selection if no matching models
        if (
            !Array.from(modelSelect.options).some(
                (option) => option.style.display === "block"
            )
        ) {
            modelSelect.value = "";
        }
    });

    // Populate input fields with row data
    function populateInputFields(data) {
        console.log("sent data:", data);
        const id = contextData.invoice;

        document.getElementById("res-value").value = data.resvalue || 0;
        document.getElementById("temp-value").value = data.itemvalueb || 0;
        document.getElementById("buy-price").value = data.orderprice || "";
        document.getElementById("sell-price").value = data.buyprice || "";
        document.getElementById("less-price").value = data.lessprice || "";
        document.getElementById("place").value = data.itemplace || "";

        document.getElementById("item-name").value = data.itemname || 0;
        document.getElementById("org-no").value = data.itemno || 0;
        document.getElementById("pno").value = data.pno || "";
        document.getElementById("invoice").value = id || "";
        document.getElementById("company-name").value =
            data.companyproduct || "";
        document.getElementById("company-no").value = data.replaceno || "";
        document.getElementById("main-cat").value = data.itemmain || "";
        document.getElementById("org-price").value = data.orgprice || "";

        //focus on input
        document.getElementById("org-price").focus();
    }
    function applyFilters(pageno = 1, pagesize = pageSize) {
        console.time("applyFiltersTime");
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
            itemno: getInputValue("org-no"),
            itemmain: getSelectedText("item-main"),
            itemsubmain: getSelectedText("item-sub-main"),
            companyproduct: getSelectedText("company"),
            itemname: getInputValue("itemname"),
            companyno: getInputValue("company-no"),
            model: getSelectedText("model"),
            country: getSelectedText("countries"),
            page: parseInt(pageno, 10) || 1,
            size: pagesize || 20,
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

        console.time("FilterTime");

        customFetch("/api/filter-items", {
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
        "itemname",
        "org-no",
        "item-main",
        "item-sub-main",
        "countries",
        "company",
        "company-no",
        "model",
    ];

    function debounce(func, wait) {
        let timeout;
        return function (...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    // Apply debounce to applyFilters with a 300ms delay
    const debouncedApplyFilters = debounce(() => applyFilters(1, pageSize), 390);
    filterInputs.forEach((inputId) => {
        document
            .getElementById(inputId)
            .addEventListener("input", () => {
                debouncedApplyFilters();
            });
    });

    document
        .getElementById("org-price")
        .addEventListener("keydown", function (event) {
            if (event.key === "Enter") {
                // Prevent default behavior if needed (e.g., form submission)
                event.preventDefault();

                // Simulate a button click or execute an action
                document.getElementById("item-value").focus();
            }
        });

    //////////////////////
    let currentPage = 1; // Tracks the current page
    let lastPage = false; // Indicates if the last page is reached
    let isLoading = false; // Prevents multiple fetch calls
    const pageSize = 100; // Number of rows per page
    const tableContainer = document.getElementById("users-table");// Table scroll container
    // Function to fetch and append the next page of data
    const fetchNextPage = () => {
        if (!lastPage) {
            currentPage++;
            console.log("currentPage : ", currentPage);
            console.log(`Fetching page ${currentPage}...`);
            console.log("fetching active url : ", active_url);

            if (active_url == "server_filtered_data") {
                console.log("apply filters current page: ", currentPage);
                applyFilters(currentPage, pageSize);
            } else {
                fetchDataFromServer({ page: currentPage, size: pageSize });
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
            debounce(fetchNextPage(), 200);
        }
    };
    function fetchDataFromServer({ page = 1, size = 100 }) {
        //console.log("isLoading: ",isLoading);
        console.time("fetchData"); // Start timer

        customFetch(`api/get-data/?page=${page}&size=${size}`, {
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
                    table.addData(data.data, false);
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
    fetchDataFromServer({ page: 1, size: 100 });

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
                applyFilters(selectedPage, selectedPageSize);
            } else {
                currentPage = selectedPage;
                fetchDataFromServer({ page: selectedPage, size: selectedPageSize });
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
            applyFilters(selectedPage, selectedPageSize);
        } else {
            fetchDataFromServer({ page: selectedPage, size: selectedPageSize });
        }
    });
    ///////////////////////
});
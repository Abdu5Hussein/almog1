document.addEventListener("DOMContentLoaded", function () {
    const jwtToken_access = (localStorage.getItem("session_data@access_token") || "").replace(/"/g, '');

    let active_url = null;
    document
        .getElementById("clear-btn")
        .addEventListener("click", clearForm);

    document
        .getElementById("export-btn-excel")
        .addEventListener("click", exportToExcel);
    document
        .getElementById("export-btn-pdf")
        .addEventListener("click", exportToPDF);

    // Function to handle mutual exclusion between checkboxes
    function handleCheckboxInteraction() {
        var check2 = document.getElementById("check2");
        var check3 = document.getElementById("check3");

        check2.addEventListener("click", function () {
            if (check2.checked) {
                // If check2 is checked, uncheck check3
                check3.checked = false;
                //console.log("check2 is checked");
                // Add your logic for check2 checked state
            }
        });

        check3.addEventListener("click", function () {
            if (check3.checked) {
                // If check3 is checked, uncheck check2
                check2.checked = false;
                //console.log("check3 is checked");
                // Add your logic for check3 checked state
            }
        });
    }

    // Trigger the initial setup
    handleCheckboxInteraction();

    // Initialize Tabulator
    // Initialize Tabulator
    const table = new Tabulator("#users-table", {
        height: "auto", // Adjust height or set a fixed height
        layout: "fitColumns",
        selectable: true,
        rowHeight: 20,
        //pagination:true, //enable pagination
        //paginationMode:"remote", //enable remote pagination
        //paginationSize: 100, // Show 100 records per page
        //paginationInitialPage: 1, // Default page
        //paginationSizeSelector: [50, 100, 200], // Page size options
        //paginationButtonCount: 5, // Number of visible pagination buttons
        //pageLoaded: function(pageNumber) {
        //  console.log("Page loaded: " + pageNumber);
        //},
        movableColumns: true,
        columnHeaderVertAlign: "bottom",
        columnMenu: true, // Enable column menu
        data: [], // Placeholder, will be loaded dynamically
        columns: [
            // Column definitions
            {
                title: "الرقم الخاص",
                field: "pno",
                headerMenu: false,
                width: 100,
                visible: true,
            },
            {
                title: "الشركة المصنعة",
                field: "companyproduct",
                headerMenu: false,
                width: 96,
                visible: true,
            },
            {
                title: "رقم الشركة",
                field: "replaceno",
                headerMenu: false,
                width: 150,
                visible: true,
            },
            {
                title: "الرقم الاصلي",
                field: "itemno",
                headerMenu: false,
                width: 90,
                visible: true,
            },
            {
                title: "اسم الصنف ع",
                field: "itemname",
                headerMenu: false,
                width: 280,
                visible: true,
            },
            {
                title: "الرصيد",
                field: "itemvalue",
                headerMenu: false,
                width: 81,
                visible: true,
            },
            {
                title: "سعر البيع",
                field: "buyprice",
                headerMenu: false,
                width: 75,
                visible: true,
            },
            {
                title: "الموقع",
                field: "itemplace",
                headerMenu: false,
                width: 75,
                visible: true,
            },
            { title: "رقم الملف", field: "fileid", visible: false },
            { title: "البيان الرئيسي", field: "itemmain", visible: false },
            { title: "البيان الفرعي", field: "itemsubmain", visible: false },
            { title: "الموديل", field: "itemthird", visible: false },
            { title: "بلد الصنع", field: "itemsize", visible: false },
            { title: "Date Product", field: "dateproduct", visible: false },
            { title: "Level Product", field: "levelproduct", visible: false },
            { title: "الرصيد الاحتياطي", field: "itemtemp", visible: false },
            { title: "تاريخ اخر طلب", field: "orderlastdate", visible: false },
            { title: "مصدر الطلب", field: "ordersource", visible: false },
            { title: "رقم فاتورة الطلب", field: "orderbillno", visible: false },
            { title: "تاريخ اخر شراء", field: "buylastdate", visible: false },
            { title: "مصدر الشراء", field: "buysource", visible: false },
            { title: "رقم فاتورة الشراء", field: "buybillno", visible: false },
            { title: "سعر التوريد", field: "orgprice", visible: false },
            { title: "سعر الشراء", field: "orderprice", visible: false },
            { title: "سعر التكلفة", field: "costprice", visible: false },
            { title: "المواصفات", field: "memo", visible: false },
            { title: "Order Stop", field: "orderstop", visible: false },
            { title: "Buy Stop", field: "buystop", visible: false },
            { title: "Item Trans", field: "itemtrans", visible: false },
            { title: "الرصيد المؤقت", field: "itemvalueb", visible: false },
            { title: "Item Type", field: "itemtype", visible: false },
            { title: "رقم الباركود", field: "barcodeno", visible: false },
            {
                title: "اسم الصنف بالانجليزي",
                field: "eitemname",
                visible: false,
            },
            { title: "عملة الشراء", field: "currtype", visible: false },
            { title: "اقل سعر", field: "lessprice", visible: false },
            { title: "قيمة العملة", field: "currvalue", visible: false },
            { title: "الرصيد المحجوز", field: "resvalue", visible: false },
            { title: "عدد القطع للصندوق", field: "itemperbox", visible: false },
            { title: "حالة الصنف", field: "cstate", visible: false },
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
        tableBuilt: function () {
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
        },
    });

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
            fetchNextPage();
        }
    };

    // Attach the scroll event listener
    tableContainer.addEventListener("scroll", handleScroll);


    fetchDataFromServer({ page: 1, size: 100 });


    table.options.tableBuilt();
    /*table.on("pageLoaded", function(pageNumber) {
        const pageSize = table.getPageSize(); // Get the current page size
      //console.log("page no: ",pageNumber);
        //console.log("page size: ",pageSize); // Fetch data for the new page
    });*/
    function fetchDataFromServer({ page = 1, size = 100 }) {
        //if (isLoading) return; // Prevent fetch if already loading
        //isLoading = true; // Set loading flag before initiating fetch

        // Use the URL in your fetch request
        console.time("fetchData"); // Start timer

        customFetch(`api/get-data/?page=${page}&size=${size}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${jwtToken_access}`,  // 👈 Include JWT token
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

                // Update the respective input fields with calculated sums
                updateIntegerInput("#itemvalue", data.total_itemvalue);
                updateIntegerInput("#tempvalueb", data.total_itemvalueb);
                updateIntegerInput("#resvalue", data.total_resvalue);

                updateSumInput("#totalcost", data.total_cost);
                updateSumInput("#totalorder", data.total_order);
                updateSumInput("#totalbuy", data.total_order);

                return data; // Return data for further processing
            })
            .catch((error) => console.error("Error fetching data:", error)).finally(() => {
                console.timeEnd("fetchData"); // End the timer regardless of success or failure
                isLoading = false; // Reset loading flag after fetch completes
                hideLoader();
            });
    }

    // Function to calculate the sum of 'itemvalue' column in Tabulator
    function calculateColumnSum(columnName) {
        const rowData = table.getData();  // Fetch row data from Tabulator

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


    function calculateProductSum(columnA, columnB) {
        let sum = 0;
        const rowData = table.getData(); // Fetch row data from Tabulator

        if (Array.isArray(rowData)) {
            // Ensure rowData is an array
            rowData.forEach((row) => {
                if (!isNaN(row[columnA]) && !isNaN(row[columnB])) {
                    const product =
                        parseFloat(row[columnA]) * parseFloat(row[columnB]);
                    sum += product; // Add the product to the sum
                }
            });
        } else {
            console.error(
                `rowData is not an array or is undefined for columns: ${columnA}, ${columnB}`
            );
        }

        return sum;
    }

    // Function to update the input field with the calculated sum
    function updateSumInput(selector, sum) {
        // Ensure 'sum' is a valid number or default to 0
        const roundedSum = (isNaN(parseFloat(sum)) ? 0 : parseFloat(sum)).toFixed(2);

        // Format the rounded number with commas
        const formattedSum = Number(roundedSum).toLocaleString("en-US", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });

        // Set the formatted sum with the unit " دل" to the input field
        $(selector).val(`${formattedSum} دل`);
    }


    function updateIntegerInput(selector, sum) {
        // Ensure 'sum' is a valid number or default to 0
        const formattedSum = parseInt(sum || 0).toLocaleString("en-US"); // Format as an integer with commas

        // Set the formatted integer value to the input field
        $(selector).val(formattedSum);
    }


    /*// Recalculate sums after the table data is loaded or updated
    table.on("dataLoaded", function () {
      console.log("Data loaded into the table");
    });

    // Optional: If filtering changes the data, you may also use the 'dataFiltered' event
    table.on("dataFiltered", function () {
      console.log("Data filtered in the table");

      // Fetch the filtered data

    });

    // You can also add event listeners to handle updates if rows are updated or added
    table.on("rowAdded", function () {

    });

    table.on("rowDeleted", function () {

    });*/

    function fetchAllData() {
        customFetch("api/get-data/", {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${jwtToken_access}`,  // 👈 Include JWT token
            }
        })
            .then((response) => response.json()) // Parse the response as JSON
            .then((data) => {
                console.log("Fetched Data:", data);
                active_url = "server_Data_No_Filter_No_pagination";
                console.log("active_url for pagination:", active_url); // Log the fetched data (optional)
                table.setData(data); // Update your table with the fetched data
            })
            .catch((error) => console.error("Error fetching data:", error)); // Handle errors
    }
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

            if (table) {
                table.clearFilter(); // Clear all filters applied
                fetchDataFromServer({ page: 1, size: pageSize });
                //console.log("Filters cleared");
            }
        });
    }
    function exportToExcel() {
        table.download("xlsx", "table_data.xlsx"); // 'xlsx' is the file format
    }

    pdfMake.fonts = {
        Amiri: {
            normal: "Amiri-Regular.ttf", // Name of the font in vfs_fonts.js
            bold: "Amiri-Regular.ttf", // Use the same if you don't have bold
            italics: "Amiri-Regular.ttf",
            bolditalics: "Amiri-Regular.ttf",
        },
    };

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
        //console.log(tableData);

        // Sending the data to Django backend using fetch
        customFetch("/generate-pdf/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                'Authorization': `Bearer ${jwtToken_access}`,
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

    // Combined filter function
    function applyFilters(pageno = 1, pagesize = pageSize) {
        console.time("applyFiltersTime");

        // Cache DOM elements for improved performance
        const filterElements = {
            itemno: document.getElementById("original-no"),
            itemmain: document.getElementById("item-main"),
            itemsubmain: document.getElementById("item-sub-main"),
            companyproduct: document.getElementById("company"),
            itemname: document.getElementById("pname-arabic"),
            companyno: document.getElementById("company-no"),
            model: document.getElementById("model"),
            country: document.getElementById("country"),
            source: document.getElementById("source"),
            fromdate: document.getElementById("from-date"),
            todate: document.getElementById("to-date"),
            check1: document.getElementById("check1"),
            check2: document.getElementById("check2"),
            check3: document.getElementById("check3"),
            check4: document.getElementById("check4"),
        };

        console.time("inputsTime");

        // Helper function to get element values
        const getValue = (element) => (element ? element.value.trim().toLowerCase() : "");
        const getSelectedText = (element) =>
            element && element.selectedIndex !== 0
                ? element.options[element.selectedIndex].text
                : "";

        // Capture filter values
        const filterValues = {
            itemno: getValue(filterElements.itemno),
            itemmain: getSelectedText(filterElements.itemmain),
            itemsubmain: getSelectedText(filterElements.itemsubmain),
            companyproduct: getSelectedText(filterElements.companyproduct),
            itemname: getValue(filterElements.itemname),
            companyno: getValue(filterElements.companyno),
            model: getSelectedText(filterElements.model),
            country: getSelectedText(filterElements.country),
            source: getSelectedText(filterElements.source),
            fromdate: getValue(filterElements.fromdate),
            todate: getValue(filterElements.todate),
            page: parseInt(pageno, 10) || 1,
            size: pagesize || 20,
        };
        console.log("filter values: ", filterValues);

        // Add additional filter conditions based on checkboxes
        if (filterElements.check1.checked) filterValues.resvalue = ">0";
        if (filterElements.check2.checked) filterValues.itemvalue = "0";
        if (filterElements.check3.checked) filterValues.itemvalue = ">0";
        if (filterElements.check4.checked) filterValues.itemvalue_itemtemp = "lte";

        console.timeEnd("inputsTime");

        // Check if all filter values are empty (except page and size)
        const isFiltersEmpty = Object.entries(filterValues).every(
            ([key, value]) => ["page", "size"].includes(key) || !value
        );

        if (isFiltersEmpty) {
            fetchDataFromServer({ page: 1, size: pageSize });
            console.timeEnd("applyFiltersTime");
            return;
        }

        // Prepare and send the request
        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";

        console.time("FilterTime");

        customFetch("/api/filter-items", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
                'Authorization': `Bearer ${jwtToken_access}`,
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

                // Update summary inputs
                updateIntegerInput("#itemvalue", data.total_itemvalue);
                updateIntegerInput("#tempvalueb", data.total_itemvalueb);
                updateIntegerInput("#resvalue", data.total_resvalue);
                updateSumInput("#totalcost", data.total_cost);
                updateSumInput("#totalorder", data.total_order);
                updateSumInput("#totalbuy", data.total_buy);
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

    // Debounce function definition
    function debounce(func, wait) {
        let timeout;
        return function (...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    // Apply debounce to applyFilters with a 300ms delay
    const debouncedApplyFilters = debounce(() => applyFilters(1), 390);


    // Add event listeners to all filter inputs
    const filterInputs = [
        "original-no",
        "item-main",
        "item-sub-main",
        "pname-arabic",
        "company",
        "company-no",
        "from-date",
        "to-date",
        "model",
        "country",
        "source",
        "check1", // Checkboxes added to the list
        "check2",
        "check3",
        "check4",
    ];

    filterInputs.forEach((inputId) => {
        document
            .getElementById(inputId)
            .addEventListener("input", () => {
                debouncedApplyFilters();
            });
    });
    // Show/Hide dropdown menu on button click
    document
        .getElementById("toggle-column-menu")
        .addEventListener("click", function () {
            const dropdown = document.getElementById("column-menu");
            dropdown.style.display =
                dropdown.style.display === "none" || dropdown.style.display === ""
                    ? "block"
                    : "none";
        });

    // Column visibility handlers (attach to checkboxes after table initialization)
    function setupColumnVisibilityHandlers(table) {
        document
            .querySelectorAll('#column-menu input[type="checkbox"]')
            .forEach((checkbox) => {
                checkbox.addEventListener("change", function () {
                    const columnField = this.value;
                    if (this.checked) {
                        table.showColumn(columnField); // Show the column
                    } else {
                        table.hideColumn(columnField); // Hide the column
                    }
                });
            });
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

});
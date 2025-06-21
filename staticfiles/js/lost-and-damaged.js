document.addEventListener("DOMContentLoaded", function () {

    // Initialize Tabulator
    const table = new Tabulator("#users-table", {
        index: "fileid", // Use "fileid" as the unique row identifier
        height: "auto", // Adjust height or set a fixed height
        layout: "fitColumns",
        selectable: true,
        //pagination: "local", // Enable local pagination
        //paginationSize: 100, // Show 100 records per page
        //paginationSizeSelector: [50, 100, 200], // Page size options
        //paginationButtonCount: 5, // Number of visible pagination buttons
        //movableColumns: true,
        columnHeaderVertAlign: "bottom",
        //columnMenu: true, // Enable column menu
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
            { title: "الرصيد الاحتياطي", field: "itemtemp", visible: false },
            { title: "سعر التوريد", field: "orgprice", visible: false },
            { title: "سعر الشراء", field: "orderprice", visible: false },
            { title: "سعر التكلفة", field: "costprice", visible: false },
            { title: "المواصفات", field: "memo", visible: false },
        ],
        placeholder: "No Data Available",
        rowFormatter: function (row) {
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
            const clickedPno = row.getData().pno; // Get pno of the clicked row
            console.log("Clicked Pno:", clickedPno);

            // Fetch data for clients_table
            customFetch(`api/get-clients/?pno=${clickedPno}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
                .then((response) => response.json())
                .then((data) => {
                    console.log("Fetched Data for Clients Table:", data);

                    // Update clients_table with the fetched data
                    clients_table.setData(data);
                })
                .catch((error) =>
                    console.error("Error fetching client data:", error)
                );
        },
        tableBuilt: function () {
            console.log("table built");
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
            itemno: getInputValue("original-no"),
            itemmain: getSelectedText("item-main"),
            itemsubmain: getSelectedText("item-sub-main"),
            companyproduct: getSelectedText("company"),
            itemname: getInputValue("pname-arabic"),
            companyno: getInputValue("company-no"),
            pno: getInputValue("pno"),
            page: parseInt(pageno, 10) || 1,
            size: pagesize || 20,
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
        "original-no",
        "item-main",
        "pname-arabic",
        "pno",
        "company-no",
        "item-sub-main",
        "company",
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
    // Handle left-click on row to populate input fields
    table.on("rowClick", function (e, row) {
        if (e.button === 2) return; // 2 is right-click
        const rowData = row.getData();
        console.log(rowData);
        const fileid = rowData.fileid; // Assuming fileid is stored in the row's data-fileid attribute
        const itemno = rowData.itemno || "لا يوجد";
        const companyno = rowData.replaceno || "لا يوجد";
        const company = rowData.companyproduct || "لا يوجد";
        const itemname = rowData.itemname || "لا يوجد";
        const costprice = rowData.costprice || "لا يوجد";
        const pno = rowData.pno || "لا يوجد";
        const itemmain = rowData.itemmain || "لا يوجد";

        if (!pno || pno == "" || pno == "لا يوجد") {
            alert("خانة الرقم الخاص PNO للصنف فارغة!");
            return;
        }
        document.getElementById("chosenProduct").value = itemname;
        document.getElementById("chosenPno").value = pno;

        sessionStorage.setItem("file-id", fileid);
        sessionStorage.setItem("itemno", itemno);
        sessionStorage.setItem("companyno", companyno);
        sessionStorage.setItem("company", company);
        sessionStorage.setItem("itemname", itemname);
        sessionStorage.setItem("costprice", costprice);
        sessionStorage.setItem("pno", pno);
        sessionStorage.setItem("itemmain", itemmain);
    });
    const confirmButton = document.getElementById("confirm-btn");
    const quantity = document.getElementById("quantity"); // Input field for the amount to add/subtract
    const radioButtons = document.querySelectorAll('input[name="status"]');
    // Add event listener to the "موافق" button
    confirmButton.addEventListener("click", function () {
        const selectedRadio = Array.from(radioButtons).find(
            (radio) => radio.checked
        );

        if (!selectedRadio) {
            alert("الرجاء اختيار الحالة (فقد / تلف)");
            return;
        }

        const status = selectedRadio.value; // either "lost" or "damaged"
        const amount = parseFloat(quantity.value.trim());

        if (isNaN(amount)) {
            alert("الرجاء ادخال الكمية.");
            return;
        }
        const fileid = sessionStorage.getItem("file-id");
        const itemno = sessionStorage.getItem("itemno");
        const companyno = sessionStorage.getItem("companyno");
        const company = sessionStorage.getItem("company");
        const itemname = sessionStorage.getItem("itemname");
        const costprice = sessionStorage.getItem("costprice");
        const pno = sessionStorage.getItem("pno");
        const itemmain = sessionStorage.getItem("itemmain");
        const today = new Date();
        const todaydate = today.toISOString();

        // Check if any of the items are null or undefined
        if (
            !fileid ||
            !itemno ||
            !companyno ||
            !company ||
            !itemname ||
            !costprice ||
            !pno
        ) {
            alert("الرجاء اختيار الصنف من الجدول لادخال فقد او تلف");
            return; // Exit the function if any required session storage item is missing
        }

        // Fetch the CSRF token from the cookies
        const getCSRFToken = () => {
            const name = "csrftoken";
            const cookies = document.cookie.split(";");
            for (let cookie of cookies) {
                if (cookie.trim().startsWith(name + "=")) {
                    return cookie.trim().split("=")[1];
                }
            }
            return null;
        };
        const valuesobj = {
            fileid: fileid,
            itemno: itemno,
            companyno: companyno,
            company: company,
            itemname: itemname,
            costprice: costprice,
            quantity: amount,
            pno: pno,
            status: status,
            date: todaydate,
            itemmain: itemmain,
        };
        console.log(valuesobj);
        const csrfToken = getCSRFToken();
        customFetch("/add-lost-damaged", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify(valuesobj),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    alert("تمت اضافة الفقد/التلف بنجاح");
                    refreshLostTable();
                    table.updateData([{ fileid: fileid, itemvalue: data.new_balance }]);
                    clearForm();
                } else {
                    alert("حدث خطأ. error: ", data.message);
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                alert("حدث خطأ");
            });

        sessionStorage.clear();
    });

    const lost_table = new Tabulator("#lost-damaged-table", {
        layout: "fitColumns",
        columns: [
            { title: "ر.م", field: "fileid", width: 50, visible: true },
            { title: "التاريخ", field: "date", width: 150, visible: true },
            {
                title: "الرقم الاصلي",
                field: "itemno",
                width: 95,
                visible: true,
            },
            {
                title: "رقم الشركة",
                field: "companyno",
                width: 120,
                visible: true,
            },
            { title: "الشركة", field: "company", width: 95, visible: true },
            {
                title: "اسم الصنف",
                field: "itemname",
                width: 200,
                visible: true,
            },
            {
                title: "الكمية",
                field: "quantity",
                hozAlign: "right",
                width: 55,
                visible: true,
            },
            {
                title: "سعر التكلفة",
                field: "costprice",
                formatter: "money",
                hozAlign: "right",
                width: 78,
                visible: true,
            },
            { title: "ر.م. للصنف", field: "pno", visible: false, width: 74 },
            { title: "رقم خاص", field: "pno_value", width: 72, visible: true },
            { title: "الحالة", field: "status", width: 70, visible: true },
            { title: "المستخدم", field: "user", width: 70, visible: true },
        ],
    });
    refreshLostTable();
    function refreshLostTable() {
        // Use the URL in your fetch request
        customFetch("/fetch-lost-damaged-data/", {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
            .then((response) => response.json())
            .then((data) => {
                console.log("Fetched lost Data:", data);

                // Set data in Tabulator
                lost_table.setData(data);

                const totalcost = calculateProductSum("quantity", "costprice");
                updateSumInput("#totalcost", totalcost);
                console.log("cost sum:", totalcost);
            })
            .catch((error) => console.error("Error fetching data:", error));
    }
    // Function to update the input field with the calculated sum
    function updateSumInput(selector, sum) {
        $(selector).val(
            sum.toLocaleString("en-US", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
            }) + " دل"
        ); // Display the sum in the input field with two decimal places
    }
    function calculateProductSum(columnA, columnB) {
        let sum = 0;
        const rowData = lost_table.getData(); // Fetch row data from Tabulator

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

    function applyFiltersForLostDamaged() {
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
            fromdate: getInputValue("from-date"),
            todate: getInputValue("to-date"),
        };

        console.log("Clients filter values:", filterValues);

        // Function to get CSRF token
        function getCSRFToken() {
            const csrfInput = document.querySelector(
                "[name=csrfmiddlewaretoken]"
            );
            return csrfInput ? csrfInput.value : "";
        }

        // Perform the fetch request
        customFetch("filter-lost-damaged", {
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
                console.log("Filtered data for lost and damaged:", data);

                // Update Tabulator table with the filtered data
                lost_table.replaceData(data);
            })
            .catch((error) => {
                console.error("Error fetching filtered data:", error);
                // Display user-friendly error message or notification
            });
    }

    // Add event listeners to all filter inputs
    const LostFilterInputs = ["from-date", "to-date"];

    LostFilterInputs.forEach((inputId) => {
        document
            .getElementById(inputId)
            .addEventListener("input", applyFiltersForLostDamaged);
    });
    document
        .getElementById("clear-btn")
        .addEventListener("click", clearForm);
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
                        if (element.type === "radio") {
                            element.checked = false; // Reset radio buttons
                        } else {
                            element.value = ""; // Reset input and textarea values
                        }
                    } else if (element.tagName.toLowerCase() === "select") {
                        element.selectedIndex = 0; // Reset select dropdowns
                    }
                }
            });

            if (table) {
                fetchDataFromServer({ page: 1, size: pageSize });
            }
            sessionStorage.clear();
        });
    }

    lost_table.on("rowClick", function (e, row) {
        if (e.button === 2) return; // 2 is right-click
        const rowData = row.getData();
        console.log(rowData);
        const fileid = rowData.fileid; // Assuming fileid is stored in the row's data-fileid attribute

        sessionStorage.setItem("delete-id", fileid);
        alert(`تم اختيار الفقد رقم ${fileid} .. اضغط حذف لحذفه`);
        console.log(fileid);
    });
    document
        .getElementById("delete-btn")
        .addEventListener("click", function () {
            const delete_id = sessionStorage.getItem("delete-id");
            // Check if any of the items are null or undefined
            if (!delete_id) {
                alert("من فضلك اضغط على الصنف المراد حذفه من الجدول");
                return; // Exit the function if any required session storage item is missing
            }
            // Show confirmation dialog
            const userConfirmed = confirm(
                `هل انت متاكد من حذف هذا الفقد/التلف رقم ${delete_id} .. اضغط موافق لحذفه`
            );
            if (!userConfirmed) {
                return; // Exit if user cancels
            }

            // Fetch the CSRF token from the cookies
            const getCSRFToken = () => {
                const name = "csrftoken";
                const cookies = document.cookie.split(";");
                for (let cookie of cookies) {
                    if (cookie.trim().startsWith(name + "=")) {
                        return cookie.trim().split("=")[1];
                    }
                }
                return null;
            };

            const csrfToken = getCSRFToken();
            customFetch("api/delete-lost-damaged", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify({
                    fileid: delete_id,
                }),
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.success) {
                        alert("تم حذف الفقد/التلف بنجاح");
                        refreshLostTable();
                    } else {
                        alert("حدث خطا اثناء الحذف. error: ", data.message);
                    }
                })
                .catch((error) => {
                    console.error("Error:", error);
                    alert("حدث خطأ.");
                });

            sessionStorage.clear();
            console.log("delete row ", delete_id);
        });

    document
        .getElementById("export-btn-excel")
        .addEventListener("click", exportToExcel);
    document
        .getElementById("export-btn-pdf")
        .addEventListener("click", exportToPDF);
    function exportToExcel() {
        lost_table.download("xlsx", "lost&damaged_data.xlsx"); // 'xlsx' is the file format
    }

    function exportToPDF() {
        // Get visible column field names
        let visibleColumns = lost_table
            .getColumns() // Retrieve column components
            .filter((col) => col.isVisible()) // Check if the column is visible
            .map((col) => col.getField()); // Get the field names of visible columns

        // Filter table data based on visible columns
        let tableData = lost_table.getData().map((row) => {
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
                    console.log("table top: ", tableContainer.scrollTop);
                    console.log("data added to the table");
                    console.log("scrollPosition: ", scrollPosition);
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
                //applyFilters(selectedPage,selectedPageSize);
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
            // applyFilters(selectedPage,selectedPageSize);
        } else {
            fetchDataFromServer({ page: selectedPage, size: selectedPageSize });
        }
    });
    ///////////////////////
});
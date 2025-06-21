document.addEventListener('DOMContentLoaded', function () {

    // Initialize Tabulator
    table = new Tabulator("#users-table", {
        height: "auto",
        layout: "fitColumns",
        selectable: true,
        rowHeight: 20,
        //pagination: "remote", // Enable local pagination
        //paginationSize: 100, // Number of rows per page
        movableColumns: true,
        columnHeaderVertAlign: "bottom",
        columnMenu: true, // Enable column menu
        rowFormatter: function (row) {
            // Set the height directly on each row
            row.getElement().style.height = "20px";
        },
        data: [], // Placeholder, will be loaded dynamically
        columns: [
            { title: "الرقم الخاص", field: "pno", headerMenu: false, width: 100, visible: true },
            { title: "الشركة المصنعة", field: "companyproduct", headerMenu: false, width: 96, visible: true },
            { title: "رقم الشركة", field: "replaceno", headerMenu: false, width: 150, visible: true },
            { title: "الرقم الاصلي", field: "itemno", headerMenu: false, width: 90, visible: true },
            { title: "اسم الصنف ع", field: "itemname", headerMenu: false, width: 280, visible: true },
            { title: "الرصيد", field: "itemvalue", headerMenu: false, width: 81, visible: true },
            { title: "سعر البيع", field: "buyprice", headerMenu: false, width: 75, visible: true },
            { title: "الموقع", field: "itemplace", headerMenu: false, width: 75, visible: true },
            { title: "سعر الشراء", field: "orderprice", visible: true, width: 75 },
            { title: "سعر التوريد", field: "orgprice", visible: true, width: 75 },
            { title: "سعر التكلفة", field: "costprice", visible: true, width: 75 },
        ],
    });

    // Allow editing of table cells
    $("#users-table").on("dblclick", ".editable", function () {
        $(this).attr("contenteditable", "true").focus();
    });

    table.on("rowClick", function (e, row) {
        console.log("Row clicked:", row.getData().pno);
        const data = row.getData();
        document.getElementById("show-pno").value = data.pno;
        document.getElementById("item_name").value = data.itemname;
        document.getElementById("show-orgprice").value = data.orgprice || "0";
        document.getElementById("show-orderprice").value = data.orderprice || "0";
        document.getElementById("show-lessprice").value = data.lessprice || "0";
        document.getElementById("show-buyprice").value = data.buyprice || "0";
        document.getElementById("show-costprice").value = data.costprice || "0";

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
                //applyFilters(currentPage, pageSize);
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
    function fetchDataFromServer({ page = 1, size = 100 }) {
        //if (isLoading) return; // Prevent fetch if already loading
        //isLoading = true; // Set loading flag before initiating fetch

        // Use the URL in your fetch request


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
    document.getElementById("apply-price-change").addEventListener("click", function () {
        const priceType = getCheckedRadioValue("price-type");
        const value = parseFloat(document.getElementById("amount").value);
        const isPercentage = document.getElementById("isPercentage").checked;
        const operation = getCheckedRadioValue("operation");

        const product_id = document.getElementById("show-pno").value; // you should define this based on selected row

        if (!priceType || isNaN(value) || !operation || !product_id) {
            alert("يجب تحديد نوع السعر، العملية، والقيمة والمنتج");
            return;
        }

        const data = {
            product_id,
            priceType,
            value,
            isPercentage,
            operation
        };

        fetch("/api/modify-price/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken() // make sure this is implemented if CSRF is enabled
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(result => {
                if (result.message) {
                    alert(result.message);
                    // Optionally reload table or update row here
                } else {
                    alert("حدث خطأ");
                    console.log(result);
                }
            })
            .catch(error => {
                console.error("Error:", error);
            }).finally(() => {
                fetchDataFromServer({ page: 1, size: 100 });
            });
    });
    function applyFilters(pageno = 1, pagesize = pageSize) {
        // Collect filter values
        const filterValues = {
            itemno: document.getElementById("original-no")?.value.trim().toLowerCase() || "",
            itemmain: document.getElementById("item-main")?.selectedIndex > 0
                ? document.getElementById("item-main").options[document.getElementById("item-main").selectedIndex].text
                : "",
            companyproduct: document.getElementById("company")?.selectedIndex > 0
                ? document.getElementById("company").options[document.getElementById("company").selectedIndex].text
                : "",
            itemname: document.getElementById("pname-arabic")?.value.trim().toLowerCase() || "",
            companyno: document.getElementById("company-no")?.value.trim().toLowerCase() || "",
            pno: document.getElementById("pno")?.value.trim().toLowerCase() || "",
            page: parseInt(pageno, 10) || 1,
            size: pagesize || pageSize,
        };

        // Checkbox filters
        if (document.getElementById("check3")?.checked) filterValues.itemvalue = ">0";
        if (document.getElementById("check1")?.checked) filterValues.resvalue = ">0";
        if (document.getElementById("check4")?.checked) filterValues.itemvalue_itemtemp = "lte";
        if (document.getElementById("check2")?.checked) filterValues.itemvalue = "0";

        // If all filters are empty, load default data
        const isFiltersEmpty = Object.entries(filterValues).every(
            ([key, value]) => ["page", "size"].includes(key) || !value
        );
        if (isFiltersEmpty) {
            fetchDataFromServer({ page: 1, size: pageSize });
            return;
        }

        // Send filter request
        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
        customFetch("/api/filter-items", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify(filterValues),
        })
            .then((response) => {
                if (!response.ok) throw new Error(`Network error: ${response.status}`);
                return response.json();
            })
            .then((data) => {
                if (pageno === 1) {
                    table.replaceData(data.data);
                    currentPage = 1;
                } else {
                    const scrollPosition = tableContainer.scrollTop;
                    table.addData(data.data);
                    tableContainer.scrollTop = scrollPosition;
                }
                lastPage = data.page_no === data.last_page;
                updatePagination(data.last_page, data.page_no);
            })
            .catch((error) => {
                console.error("Error fetching filtered data:", error.message);
            })
            .finally(() => {
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
        "company",
        "company-no",
        "pno",
    ];
    const filterRadios = [
        "check1",
        "check2",
        "check3",
        "check4",
    ];

    filterInputs.forEach((inputId) => {
        document
            .getElementById(inputId)
            .addEventListener("input", () => {
                applyFilters();
            });
    });
    filterRadios.forEach((inputId) => {
        document
            .getElementById(inputId)
            .addEventListener("change", () => {
                applyFilters();
            });
    });
});
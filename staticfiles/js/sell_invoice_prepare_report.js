document.addEventListener("DOMContentLoaded", function () {

    const invoices_table = new Tabulator("#invoices-table", {
        index: "invoice_no",
        height: "auto",
        layout: "fitColumns",
        selectable: true,
        columnHeaderVertAlign: "bottom",
        data: [],
        columns: [
            { title: "تاريخ الاعداد", field: "invoice_date", width: 160 },
            { title: "رقم الفاتورة", field: "invoice_no", headerSort: false, width: 100 },
            { title: "اسم العميل", field: "client_name", width: 100 },
            { title: "أمر التسليم", field: "deliver_request", width: 90 },
            { title: "حالة الفاتورة", field: "invoice_status", width: 90 },
            { title: "ملاحظات", field: "notes", width: 100 }
        ],
        placeholder: "No Data Available",
        rowFormatter: function (row) {
            var rowData = row.getData();
            switch (rowData.invoice_status) {
                case "لم تحضر": row.getElement().style.backgroundColor = "#fdffff"; break;
                case "جاري التحضير": row.getElement().style.backgroundColor = "#fffd82"; break;
                case "روجعت": row.getElement().style.backgroundColor = "#f9a990"; break;
                case "سلمت": row.getElement().style.backgroundColor = "#00fe81"; break;
                case "سلمت جزئيا": row.getElement().style.backgroundColor = "#7f8000"; break;
                case "ترجيع كلي": row.getElement().style.backgroundColor = "#d5fef0"; break;
                case "ترجيع جزئي": row.getElement().style.backgroundColor = "#dee7a0"; break;
            }
        },
        rowClick: function (e, row) {
            const clickedPno = row.getData().pno;
            console.log("Clicked Pno:", clickedPno);
        },
        tableBuilt: function () {
            console.log("table built");
        },
    });

    function getCSRFToken() {
        const csrfInput = document.querySelector("[name=csrfmiddlewaretoken]");
        return csrfInput ? csrfInput.value : "";
    }

    let childWindows = [];
    function openWindow(url, width = 600, height = 700) {
        const parentWidth = window.innerWidth;
        const parentHeight = window.innerHeight;
        const parentLeft = window.screenX;
        const parentTop = window.screenY;
        const left = parentLeft + (parentWidth - width) / 2;
        const top = parentTop + (parentHeight - height) / 2;
        const childWindow = window.open(
            url,
            "_blank",
            `width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=yes`
        );
        if (!childWindow) {
            alert("Pop-up blocked! Please allow pop-ups for this website.");
            return;
        }
        childWindows.push(childWindow);
        const monitorChild = setInterval(() => {
            if (childWindow.closed) {
                childWindows = childWindows.filter((win) => win !== childWindow);
                clearInterval(monitorChild);
            }
        }, 300);
        window.onbeforeunload = function () {
            childWindows.forEach((win) => {
                if (!win.closed) {
                    win.close();
                }
            });
        };
    }

    invoices_table.on("rowClick", function (e, row) {
        const hasInvoicePreparePermission = document.getElementById("hasInvoicePreparePermission").value;
        if (!hasInvoicePreparePermission) {
            alert("لا تملك صلاحية تحضير الفاتورة");
            return;
        }
        console.log("Row clicked:", row.getData().autoid);
        const id = row.getData().invoice_no;
        console.log("sent id: ", id);
        openWindow("sell_invoice_storage_manage?inv=" + id, 1000, 700);
    });

    let currentInvoicesPage = 1;
    let lastInvoicesPage = false;
    let isLoading = false;
    const pageSize = 100;
    const invoicesTableContainer = document.getElementById("invoices-table");

    const fetchNextPageForInvoices = () => {
        if (!lastInvoicesPage) {
            currentInvoicesPage++;
            console.log(`Fetching page ${currentInvoicesPage}...`);
            console.log("fetching active url : ", active_url);
            if (active_url == "server_filtered_data") {
                applyFiltersForInvoices(currentInvoicesPage, pageSize);
            } else {
                fetchInvoicesFromServer({ page: currentInvoicesPage, size: pageSize });
            }
        }
    };

    const handleScrollForInvoices = () => {
        const scrollPosition = invoicesTableContainer.scrollTop + invoicesTableContainer.clientHeight;
        const scrollThreshold = invoicesTableContainer.scrollHeight - 2000;
        console.log("isLoading: ", isLoading);
        console.log("lastInvoicesPage: ", lastInvoicesPage);
        if (scrollPosition >= scrollThreshold && !lastInvoicesPage && !isLoading) {
            console.log("scrollPosition: ", scrollPosition);
            console.log("scrollThreshold: ", scrollThreshold);
            console.log("scrollHeight: ", invoicesTableContainer.scrollHeight);
            isLoading = true;
            showInvoicesLoader();
            fetchNextPageForInvoices();
        }
    };

    function updateInput(id, value) {
        document.getElementById(id).value = value;
    }

    function fetchInvoicesFromServer({ page = 1, size = 100 }) {
        console.time("fetchData");
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
                console.time("tableTime");
                if (page === 1) {
                    invoices_table.setData(data.data);
                    console.log("data set to the table");
                    currentInvoicesPage = 1;
                } else {
                    let scrollPosition = invoicesTableContainer.scrollTop;
                    invoices_table.addData(data.data);
                    invoicesTableContainer.scrollTop = scrollPosition;
                    console.log("data added to the table");
                }
                console.timeEnd("tableTime");
                lastInvoicesPage = data.page_no == data.last_page ? true : false;
                console.time("PaginationTime");
                updateInvoicesPagination(data.last_page, data.page_no);
                console.timeEnd("PaginationTime");
                return data;
            })
            .catch((error) => console.error("Error fetching data:", error))
            .finally(() => {
                console.timeEnd("fetchData");
                isLoading = false;
                hideInvoicesLoader();
            });
    }

    invoicesTableContainer.addEventListener("scroll", handleScrollForInvoices);

    function debounce(func, wait) {
        let timeout;
        return function (...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    applyFiltersForInvoices({ page: 1, size: 100 });
    setInterval(function () {
        const liveStopCheckbox = document.getElementById("live-stop");
        if (!liveStopCheckbox.checked) {
            applyFiltersForInvoices(1, 100);
        }
    }, 3000);

    function showInvoicesLoader() {
        const loader = document.getElementById("invoices-loader-element");
        loader.classList.remove("d-none");
        loader.classList.add("d-flex");
    }

    function hideInvoicesLoader() {
        const loader = document.getElementById("invoices-loader-element");
        setTimeout(function () {
            loader.classList.remove("d-flex");
            loader.classList.add("d-none");
        }, 3000);
    }

    function updateInvoicesPagination(lastInvoicesPage, currentInvoicesPage) {
        const pagination = document.querySelector(".invoices-pagination");
        const existingPageLinks = pagination.querySelectorAll(".invoices-page-item:not(:first-child):not(:last-child):not(#invoices-page-size)");
        const startPage = Math.max(1, currentInvoicesPage);
        const endPage = Math.min(lastInvoicesPage, startPage + 2);
        let index = 0;
        for (let i = startPage; i <= endPage; i++) {
            let pageItem;
            if (index < existingPageLinks.length) {
                pageItem = existingPageLinks[index];
                pageItem.querySelector(".invoices-page-link").innerText = i;
                pageItem.querySelector(".invoices-page-link").setAttribute("data-page", i);
            } else {
                pageItem = document.createElement("li");
                pageItem.className = "invoices-page-item";
                pageItem.innerHTML = `<a class="invoices-page-link" href="#" data-page="${i}">${i}</a>`;
                pagination.insertBefore(pageItem, pagination.querySelector("li:last-child"));
            }
            pageItem.querySelector(".invoices-page-link").classList.toggle("page-link-active", i === currentInvoicesPage);
            index++;
        }
        const previousBtn = document.querySelector(".invoices-page-prev");
        previousBtn.classList.toggle("item-disabled", currentInvoicesPage === 1);
        previousBtn.querySelector(".invoices-page-link").setAttribute("data-page", currentInvoicesPage - 1);
        const nextBtn = document.querySelector(".invoices-page-next");
        nextBtn.classList.toggle("item-disabled", currentInvoicesPage === endPage);
        nextBtn.querySelector(".invoices-page-link").setAttribute("data-page", currentInvoicesPage + 1);
        const firstBtn = document.querySelector(".invoices-page-first");
        firstBtn.querySelector(".invoices-page-link").setAttribute("data-page", 1);
        const lastBtn = document.querySelector(".invoices-page-last");
        lastBtn.querySelector(".invoices-page-link").setAttribute("data-page", lastInvoicesPage);
        document.getElementById("invoices-page-total").innerHTML = "تم تحميل " + currentInvoicesPage + " من اجمالي " + lastInvoicesPage + " صفحات ";
    }

    document.querySelector(".invoices-pagination").addEventListener("click", function (event) {
        const target = event.target;
        if (
            target.classList.contains("invoices-page-link") &&
            !target.parentNode.classList.contains("disabled") &&
            !target.closest("#page-size")
        ) {
            event.preventDefault();
            const selectedPage = parseInt(target.getAttribute("data-page"), 10);
            const selectedPageSize = document.getElementById("page-size").value;
            if (lastInvoicesPage) {
                return;
            }
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

    document.querySelector("#invoices-page-size").addEventListener("change", function () {
        const selectedPageSize = this.value;
        const selectedPage = document.querySelector(".invoices-page-link.page-link-active").innerHTML;
        console.log(`Fetching data for page: ${selectedPage}, with page size ${selectedPageSize}, for ${active_url}`);
        if (active_url == "server_filtered_data") {
            applyFiltersForInvoices(selectedPage, selectedPageSize);
        } else {
            fetchInvoicesFromServer({ page: selectedPage, size: selectedPageSize });
        }
    });

    function applyFiltersForInvoices(pageno = 1, pagesize = pageSize) {
        console.time("applyFiltersTime");
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
            const checkedRadio = document.querySelector(`input[name="${name}"]:checked`);
            return checkedRadio ? checkedRadio.value : null;
        }
        const filterValues = {
            client: getSelectedText("client"),
            fromdate: getInputValue("from-date"),
            todate: getInputValue("to-date"),
            invoice_no: getInputValue("invoice-no"),
            page: parseInt(pageno, 10) || 1,
            size: pagesize || 20,
        };
        console.log("Filter values:", filterValues);
        function getCSRFToken() {
            const csrfInput = document.querySelector("[name=csrfmiddlewaretoken]");
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
            });
    }
    function CustomApplyFiltersForInvoices(pageno = 1, pagesize = pageSize) {
        console.time("applyFiltersTime");
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
            const checkedRadio = document.querySelector(`input[name="${name}"]:checked`);
            return checkedRadio ? checkedRadio.value : null;
        }
        const filterValues = {
            client: getSelectedText("client"),
            //fromdate: getInputValue("from-date"),
            //todate: getInputValue("to-date"),
            invoice_no: getInputValue("invoice-no"),
            page: parseInt(pageno, 10) || 1,
            size: pagesize || 20,
        };
        console.log("Filter values:", filterValues);
        function getCSRFToken() {
            const csrfInput = document.querySelector("[name=csrfmiddlewaretoken]");
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
            });
    }

    const filterInputsForInvoices = [
        "client",
        "from-date",
        "to-date",
        // "invoice-no",
    ];

    document.getElementById("invoice-no").addEventListener("input", function () {
        CustomApplyFiltersForInvoices(1, pageSize);
    });

    function debounce(func, wait) {
        let timeout;
        return function (...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    const debouncedApplyFiltersForInvoices = debounce(() => applyFiltersForInvoices(1, pageSize), 390);
    filterInputsForInvoices.forEach((inputId) => {
        document
            .getElementById(inputId)
            .addEventListener("input", () => {
                debouncedApplyFiltersForInvoices();
            });
    });

    document.getElementById("all-btn").addEventListener("click", clearForm);
    document.getElementById("clear-btn").addEventListener("click", clearForm);

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
                            element.checked = false;
                        } else {
                            element.value = "";
                        }
                    } else if (tagName === "select") {
                        element.selectedIndex = 0;
                    }
                }
            });
            if (invoices_table) {
                invoices_table.clearFilter();
                fetchInvoicesFromServer({ page: 1, size: 100 });
            }
        });
    }

    function updateCalc() { }

    document.getElementById("export-btn-excel").addEventListener("click", exportToExcel);
    document.getElementById("export-btn-pdf").addEventListener("click", exportToPDF);

    function exportToExcel() {
        invoices_table.download("xlsx", "table_data.xlsx");
    }

    function exportToPDF() {
        let visibleColumns = invoices_table
            .getColumns()
            .filter((col) => col.isVisible())
            .map((col) => col.getField());
        let tableData = invoices_table.getData().map((row) => {
            return visibleColumns.reduce((filteredRow, field) => {
                filteredRow[field] = row[field];
                return filteredRow;
            }, {});
        });
        customFetch("/generate-pdf/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                data: tableData,
            }),
        })
            .then((response) => response.blob())
            .then((blob) => {
                const file = new Blob([blob], { type: "application/pdf" });
                const fileURL = URL.createObjectURL(file);
                const link = document.createElement("a");
                link.href = fileURL;
                link.download = "tabulator_data.pdf";
                link.click();
            })
            .catch((error) => {
                console.error("Error:", error);
            });
    }

    function filterStatus(input, pageno = 1, pagesize = 100) {
        let status = "";
        switch (input) {
            case "لم تحضر":
            case "جاري التحضير":
            case "روجعت":
            case "سلمت":
            case "سلمت جزئيا":
            case "ترجيع كلي":
            case "ترجيع جزئي":
                status = input;
                break;
            default:
                console.log("error");
                return;
        }
        if (status !== "") {
            const filterValues = {
                invoice_status: status,
            };
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
                    console.log("response: ", data);
                    console.log("filter data", data.data);
                    if (typeof invoices_table !== "undefined" && typeof invoicesTableContainer !== "undefined") {
                        if (pageno === 1) {
                            invoices_table.replaceData(data.data);
                            currentInvoicesPage = 1;
                        } else {
                            const scrollPosition = invoicesTableContainer.scrollTop;
                            invoices_table.addData(data.data);
                            invoicesTableContainer.scrollTop = scrollPosition;
                        }
                    }
                    lastInvoicesPage = data.page_no === data.last_page;
                    updateInvoicesPagination(data.last_page, data.page_no);
                })
                .catch((error) => {
                    console.error("Error fetching filtered data:", error.message);
                })
                .finally(() => {
                    active_url = "server_filtered_data";
                    isLoading = false;
                    hideInvoicesLoader();
                });
        }
    }

    document.getElementById("btn-1").addEventListener("click", function () {
        filterStatus("لم تحضر");
    });
    document.getElementById("btn-2").addEventListener("click", function () {
        filterStatus("جاري التحضير");
    });
    document.getElementById("btn-3").addEventListener("click", function () {
        filterStatus("روجعت");
    });
    document.getElementById("btn-4").addEventListener("click", function () {
        filterStatus("سلمت");
    });
    document.getElementById("btn-5").addEventListener("click", function () {
        filterStatus("سلمت جزئيا");
    });
    document.getElementById("btn-6").addEventListener("click", function () {
        filterStatus("ترجيع كلي");
    });
    document.getElementById("btn-7").addEventListener("click", function () {
        filterStatus("ترجيع جزئي");
    });
});
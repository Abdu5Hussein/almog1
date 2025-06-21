document.addEventListener("DOMContentLoaded", function () {

    // Initialize Tabulator
    const table = new Tabulator("#users-table", {
        index: "clientid", // Use "clientid" as the unique row identifier
        height: "auto",
        layout: "fitColumns",
        selectable: true,
        columnHeaderVertAlign: "bottom",
        data: [],
        columns: [
            { title: "رقم المورد", field: "clientid", sorter: "number", visible: true, width: 100 },
            { title: "اسم المورد", field: "name", sorter: "string", visible: true, width: 200 },
            { title: "العنوان", field: "address", sorter: "string", visible: true, width: 200 },
            { title: "البريد الإلكتروني", field: "email", sorter: "string", visible: true, width: 150 },
            { title: "الهاتف", field: "phone", sorter: "string", visible: true, width: 100 },
            { title: "عملة الحساب", field: "accountcurr", sorter: "string", visible: true, width: 100 },
            { title: "العمولة", field: "commission", sorter: "number", visible: true, width: 100 },
        ],
        placeholder: "No Data Available",
        rowClick: function (e, row) {
            const rowData = row.getData();
            populateInputFields(rowData);
        },
        tableBuilt: function () {
            // Table built callback
        },
    });

    refreshTable();

    function refreshTable({ page = 1, size = 100 } = {}) {
        //showLoader();
        customFetch(`/api/sources-api/?page=${page}&size=${size}`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        })
            .then((response) => response.json())
            .then((data) => {
                table.setData(data.data || data); // Use .results if paginated, else data
                updatePagination(data.last_page || 1, data.page_no || 1);
            })
            .catch((error) => console.error("Error fetching data:", error))
            .finally(() => {
                hideLoader();
            });
    }

    function getCSRFToken() {
        return document.querySelector("[name=csrfmiddlewaretoken]").value;
    }
    table.on("rowClick", function (e, row) {
        const clientId = row.getData().clientid;
        if (!clientId) return;
        //showLoader();
        customFetch(`/api/sources-api/${clientId}/`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        })
            .then((response) => response.json())
            .then((data) => {
                populateInputFields(data);
            })
            .catch((error) => console.error("Error fetching details:", error))
            .finally(() => {
                hideLoader();
            });
    });

    function populateInputFields(data) {
        console.log("Populating input fields with data");
        // If data is a DRF serializer response, use .data property if present
        const d = data && data.data ? data.data : data;
        document.getElementById("cname-arabic").value = d.name || "";
        document.getElementById("cno").value = d.clientid || "";
        document.getElementById("address").value = d.address || "";
        document.getElementById("email").value = d.email || "";
        document.getElementById("website").value = d.website || "";
        document.getElementById("phone-no").value = d.phone || "";
        document.getElementById("mobile-no").value = d.mobile || "";
        document.getElementById("last-history").value = d.last_transaction_details || "";
        document.getElementById("limit").value = d.loan_period || "";
        document.getElementById("limit-value").value = d.loan_limit || "";
        document.getElementById("text-area").value = d.other || "";
        document.getElementById("password").value = "";
        document.getElementById("password2").value = "";
        // Set selects
        setSelectByValue("currency", d.accountcurr);
        setSelectByValue("sub-category", d.category);
        setSelectByValue("installments", d.loan_day);
        setSelectByValue("types", d.subtype);
        // Set checkboxes
        document.getElementById("client-stop").checked = !!d.client_stop;
        document.getElementById("account-type").checked = !!d.curr_flag;
        // Permissions
        setPermissionCheckboxes(d.permissions);
        // Username/commission
        if (document.getElementById("username")) document.getElementById("username").value = d.username || "";
        if (document.getElementById("commission")) document.getElementById("commission").value = d.commission || "";
    }

    function setSelectByValue(id, value) {
        const select = document.getElementById(id);
        if (!select) return;
        for (let i = 0; i < select.options.length; i++) {
            if (select.options[i].value == value || select.options[i].text == value) {
                select.selectedIndex = i;
                return;
            }
        }
        select.selectedIndex = 0;
    }

    function setPermissionCheckboxes(permissions) {
        const perms = (permissions || "").split(";");
        ["sales", "purchases", "stock", "client-reports"].forEach(id => {
            const cb = document.getElementById(id);
            if (cb) cb.checked = perms.includes(id);
        });
    }

    // Permissions string builder
    function getPermissionsString() {
        let perms = [];
        ["sales", "purchases", "stock", "client-reports"].forEach(id => {
            const cb = document.getElementById(id);
            if (cb && cb.checked) perms.push(id);
        });
        return perms.join(";");
    }

    document.getElementById("new-record-button").addEventListener("click", function (event) {
        event.preventDefault();
        createOrUpdateRecord("POST");
    });

    document.getElementById("update-record-button").addEventListener("click", function (event) {
        event.preventDefault();
        createOrUpdateRecord("PUT");
    });

    function createOrUpdateRecord(method) {
        const phone = document.getElementById("phone-no")?.value;
        const name = document.getElementById("cname-arabic")?.value;
        if (!phone || !name) {
            alert("الرجاء ادخال اسم ورقم هاتف المورد");
            return;
        }
        const data = {
            csrfmiddlewaretoken: getCSRFToken(),
            clientid: document.getElementById("cno")?.value || "",
            name: document.getElementById("cname-arabic")?.value || "",
            address: document.getElementById("address")?.value || "",
            email: document.getElementById("email")?.value || "",
            website: document.getElementById("website")?.value || "",
            phone: document.getElementById("phone-no")?.value || "",
            mobile: document.getElementById("mobile-no")?.value || "",
            last_transaction_details: document.getElementById("last-history")?.value || "",
            accountcurr: document.getElementById("currency")?.value || "",
            type: "", // Not present in form, set as needed
            category: document.getElementById("sub-category")?.value || "",
            loan_period: document.getElementById("limit")?.value || null,
            loan_limit: document.getElementById("limit-value")?.value || "",
            loan_day: document.getElementById("installments")?.value || "",
            subtype: document.getElementById("types")?.value || "",
            client_stop: document.getElementById("client-stop")?.checked || false,
            curr_flag: document.getElementById("account-type")?.checked || false,
            permissions: getPermissionsString(),
            other: document.getElementById("text-area")?.value || "",
            username: document.getElementById("username")?.value || "",
            password: document.getElementById("password")?.value || "",
            commission: document.getElementById("commission")?.value || "",
        };
        let url = "/api/sources-api/";
        if (method === "PUT") {
            const clientid = document.getElementById("cno")?.value || "";
            if (!clientid) {
                alert("يرجى اختيار مورد للتعديل");
                return;
            }
            url = `/api/sources-api/${clientid}/`;
        }
        customFetch(url, {
            method: method,
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify(data),
        })
            .then((response) => {
                if (response.ok) {
                    alert(method === "POST" ? "تم اضافة المورد بنجاح!" : "تم تعديل المورد بنجاح!");
                    refreshTable();
                } else {
                    return response.json().then((data) => {
                        alert("حدث خطأ: " + (data.message || "Unknown error"));
                    });
                }
            })
            .catch((error) => {
                alert("An error occurred, " + error.message);
            });
    }

    document.getElementById("deleteButton").addEventListener("click", function (event) {
        event.preventDefault();
        const confirmation = window.confirm("هل أنت متأكد من أنك تريد حذف هذا السجل؟");
        if (!confirmation) return;
        const clientid = document.getElementById("cno")?.value || "";
        if (!clientid) {
            alert("يرجى اختيار مورد للحذف");
            return;
        }
        customFetch(`/api/sources-api/${clientid}/`, {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({ csrfmiddlewaretoken: getCSRFToken(), clientid }),
        })
            .then((response) => {
                if (response.ok) {
                    alert("تم حذف المورد بنجاح!");
                    refreshTable();
                } else {
                    alert("حدث خطأ أثناء الحذف.");
                }
            })
            .catch((error) => console.error("Error:", error));
    });

    document.getElementById("clear-btn").addEventListener("click", clearForm);
    function clearForm() {
        window.requestAnimationFrame(function () {
            const formElements = document.querySelectorAll("form input, form select, form textarea");
            formElements.forEach(function (element) {
                if (!element.classList.contains("value-fixed")) {
                    if (element.type === "checkbox" || element.type === "radio") {
                        element.checked = false;
                    } else {
                        element.value = "";
                    }
                    if (element.tagName.toLowerCase() === "select") {
                        element.selectedIndex = 0;
                    }
                }
            });
        });
    }

    // Pagination and loader helpers (same as before)
    function showLoader() {
        const loader = document.getElementById("loader-element");
        loader.classList.remove("d-none");
        loader.classList.add("d-flex");
    }
    function hideLoader() {
        const loader = document.getElementById("loader-element");
        setTimeout(function () {
            loader.classList.remove("d-flex");
            loader.classList.add("d-none");
        }, 1000);
    }
    function updatePagination(lastPage, currentPage) {
        document.getElementById("page-total").innerHTML = "تم تحميل " + currentPage + " من اجمالي " + lastPage + " صفحات ";
    }
});
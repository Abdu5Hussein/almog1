document.addEventListener('DOMContentLoaded', function () {
    const employees_table = new Tabulator("#employees-table", {
        layout: "fitColumns",
        height: "100%",
        selectable: 1,

        columns: [
            { title: "رقم الموظف", field: "employee_id", hozAlign: "center", width: 120 },
            { title: "اسم الموظف", field: "name", hozAlign: "right" },
            {
                title: "المرتب الشهري",
                field: "salary",
                hozAlign: "center",
                editor: "input",
                formatter: function (cell) {
                    let value = cell.getValue();
                    if (value == null || isNaN(value)) {
                        return "د.ل 0";
                    }
                    return `د.ل ${Number(value).toLocaleString()}`;
                }
            },
            {
                title: "الرصيد",
                field: "balance",
                hozAlign: "center",
                formatter: function (cell) {
                    let value = cell.getValue();
                    if (value == null || isNaN(value)) {
                        return "د.ل 0";
                    }
                    return `د.ل ${Number(value).toLocaleString()}`;
                }
            }
        ],
        placeholder: "No Data Available",

        rowClick: function (e, row) {
            selectedRow = row;
        }
    });

    // Load data
    function loadEmployeeData() {
        customFetch("/api/employees-api")
            .then(response => response.json())
            .then(data => {
                employees_table.setData(data.results);
            })
            .catch(error => {
                console.error("Failed to fetch employee data:", error);
            });
    }
    function loadEditionsData(id) {
        customFetch("/api/balance-editions/user/" + id)
            .then(response => response.json())
            .then(data => {
                salaries_table.setData(data);
            })
            .catch(error => {
                console.error("Failed to fetch employee data:", error);
            });
    }
    function clearForm() {
        window.requestAnimationFrame(function () {
            const formElements = document.querySelectorAll(
                " input,  select,  textarea"
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

                loadEmployeeData();
            });
        });
    }
    document.addEventListener("DOMContentLoaded", function () {
        loadEmployeeData();
    });
    document.getElementById("clear-btn").addEventListener("click", function () {
        clearForm();
    });
    document.getElementById("submit-btn").addEventListener("click", function () {
        submitBalanceEdition();
    });
    document.getElementById("delete-btn").addEventListener("click", function () {
        deleteBalanceEdition();
    });
    const salaries_table = new Tabulator("#salaries-table", {
        data: [], // or use ajaxURL: '/your-endpoint' for dynamic data
        layout: "fitColumns",
        height: "100%",
        columns: [
            { title: "ر. المعاملة", field: "id", hozAlign: "center" },
            { title: "التاريخ", field: "date", hozAlign: "center" },
            { title: "القيمة", field: "amount", hozAlign: "center", formatter: "money", formatterParams: { symbol: "د.ل", precision: 0 } },
            { title: "بيان التسوية", field: "description" },
            { title: "نوع التسوية", field: "type" },
        ],
        placeholder: "No Data Available",
    });

    employees_table.on("rowClick", function (e, row) {
        console.log("Row clicked after data update:", row.getData());
        const employee_id = row.getData().employee_id; // Get pno of the clicked row
        console.log("Clicked employee_id:", employee_id);

        loadEditionsData(employee_id);
    });

    function submitBalanceEdition() {
        const employeeId = document.getElementById("client").value;
        const description = document.getElementById("description").value;
        const amount = document.getElementById("amount").value;
        const transactionTypeArabic = document.querySelector('input[name="transactionType"]:checked');

        if (!employeeId || !amount || !transactionTypeArabic) {
            alert("يرجى تعبئة جميع الحقول المطلوبة.");
            return;
        }

        // Map Arabic to English values
        const typeMap = {
            "دائن": "credit",
            "مدين": "debit"
        };
        const type = typeMap[transactionTypeArabic.value];

        const payload = {
            employee: parseInt(employeeId),
            amount: parseFloat(amount),
            type: type,
            description: description,
            name: description  // You can change this mapping if needed
        };
        console.log(payload);

        customFetch("/api/balance-editions-api/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                // "X-CSRFToken": csrftoken, // Uncomment if needed with csrf protection
            },
            body: JSON.stringify(payload)
        })
            .then(response => {
                if (!response.ok) throw new Error("Network response was not ok");
                return response.json();
            })
            .then(data => {
                console.log("Success:", data);
                alert("تمت إضافة الحركة بنجاح");
                // Optionally reset fields or reload data
            })
            .catch(error => {
                console.error("Error:", error);
                alert("حدث خطأ أثناء الإرسال.");
            });
    }
    function deleteBalanceEdition() {
        const id = prompt("أدخل رقم المعاملة التي تريد حذفها:");
        if (!id) {
            alert("لم يتم إدخال رقم.");
            return;
        }

        if (confirm(`هل أنت متأكد أنك تريد حذف المعاملة رقم ${id}؟`)) {
            fetch(`/api/balance-editions-api/${id}/`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()  // If using Django with CSRF protection
                }
            })
                .then(response => {
                    if (response.ok) {
                        alert("تم الحذف بنجاح.");
                        location.reload(); // Optional: reload page after delete
                    } else {
                        return response.json().then(data => {
                            throw new Error(data.detail || "حدث خطأ أثناء الحذف.");
                        });
                    }
                })
                .catch(error => {
                    alert(error.message);
                });
        }
    }
});
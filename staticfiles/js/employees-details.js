document.addEventListener('DOMContentLoaded', function () {

    let selectedRow = null;

    // Initialize Tabulator
    const employees_table = new Tabulator("#employees-table", {
        layout: "fitColumns",
        height: "100%",
        selectable: 1,
        columns: [
            { title: "رقم الموظف", field: "employee_id", hozAlign: "center", width: 120 },
            { title: "اسم الموظف", field: "name", hozAlign: "right" },
            { title: "رقم الهاتف", field: "phone", hozAlign: "center" },
            { title: "القسم", field: "type", hozAlign: "center" },
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
                console.log(data);
            })
            .catch(error => {
                console.error("Failed to fetch employee data:", error);
            });
    }

        loadEmployeeData();


    // Add
    document.getElementById('add-btn').addEventListener('click', async function () {

        /* 1- التحقّق من حقول الاسم والهاتف */
        if (!document.getElementById('name').value ||
            !document.getElementById('phone').value) {
            alert('الرجاء إدخال اسم ورقم هاتف الموظف');
            return;
        }

        /* 2- تجهيز بيانات إنشاء الموظّف (بلا صور) */
        const today = new Date();
        const startDate = document.getElementById('start_date').value.trim();
        const endDate = document.getElementById('end_date').value.trim();
        const employeeObj = {
            name: document.getElementById('name').value,
            nationality: document.getElementById('nationality').value,
            identity_doc: document.getElementById('identity_doc').value,
            address: document.getElementById('address').value,
            phone: document.getElementById('phone').value,
            type: document.getElementById('type').value,
            salary: parseFloat(document.getElementById('salary').value) || 0,
            last_transaction: document.getElementById('last_transaction').value,
            start_date: startDate === '' ? today.toISOString().split('T')[0] : startDate,
            end_date: endDate === '' ? new Date(today.setFullYear(today.getFullYear() + 1))
                .toISOString().split('T')[0] : endDate
        };

        const employeeImage = document.getElementById('employee_image').files[0] || null;
        const contractImage = document.getElementById('contract_image').files[0] || null;

        try {
            /* 3- إنشاء الموظّف (طلب JSON) */
            const createRes = await customFetch('/api/employees-api/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',              // لإرسال الـ Cookie الخاصّة بالجلسة
                body: JSON.stringify(employeeObj)
            });

            if (!createRes.ok) throw new Error('فشل إضافة الموظف');
            const created = await createRes.json();        // نتوقّع { employee_id: … }
            const empId = created.employee.employee_id;

            /* 4- رفع الصورة بعد التأكّد من وجودها */
            if (employeeImage) {
                const imgForm = new FormData();
                imgForm.append('employee_image', employeeImage);
                const imgRes = await fetch(`/employees/${empId}/upload-image/`, {
                    method: 'POST',
                    body: imgForm,
                    credentials: 'include'
                });
                if (!imgRes.ok) throw new Error('فشل رفع صورة الموظف');
            }

            /* 5- رفع صورة العقد إذا أردت (مسار مشابه إن أنشأته في الباكенд) */
            if (contractImage) {
                const contractForm = new FormData();
                contractForm.append('contract_image', contractImage);
                await fetch(`/employees/${empId}/upload-contract/`, {    // أنشئ هذا المسار إن لزم
                    method: 'POST',
                    body: contractForm,
                    credentials: 'include'
                });
            }

            clearForm();           // دالة تفريغ الحقول إن كانت لديك
            alert('تم إضافة الموظف ورفع الصور بنجاح');

        } catch (err) {
            console.error(err);
            alert(err.message || 'حدث خطأ غير متوقَّع؛ حاول مجددًا');
        }
    });

    document.getElementById('edit-btn').addEventListener("click", function () {
        const id = document.getElementById("employee_id").value;
        if (!id) {
            alert("اختر موظفًا أولاً");
            return;
        }

        const today = new Date();
        const start_date = (document.getElementById("start_date").value.trim() === "")
            ? today.toISOString().split('T')[0]
            : document.getElementById("start_date").value;

        const end_date = (document.getElementById("end_date").value.trim() === "")
            ? new Date(today.setFullYear(today.getFullYear() + 1)).toISOString().split('T')[0]
            : document.getElementById("end_date").value;

        const updatedEmployee = {
            name: document.getElementById("name").value,
            nationality: document.getElementById("nationality").value,
            identity_doc: document.getElementById("identity_doc").value,
            address: document.getElementById("address").value,
            phone: document.getElementById("phone").value,
            type: document.getElementById('type').value,
            salary: parseFloat(document.getElementById("salary").value) || 0,
            last_transaction: document.getElementById("last_transaction").value,
            start_date: start_date,
            end_date: end_date
        };

        // Step 1: Update JSON data
        customFetch(`/api/employees-api/${id}/`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(updatedEmployee)
        })
            .then(res => {
                if (!res.ok) throw new Error("Update failed");
                return res.json();
            })
            .then(() => {
                // Step 2: Upload employee image (if selected)
                const empImageFile = document.getElementById("employee_image").files[0];
                if (empImageFile) {
                    const empForm = new FormData();
                    empForm.append("employee_image", empImageFile);

                    return fetch(`/employees/${id}/upload-image/`, {
                        method: "POST",
                        credentials: "include",
                        body: empForm
                    });
                }
            })
            .then(() => {
                // Step 3: Upload contract image (if selected)
                const contractFile = document.getElementById("contract_image").files[0];
                if (contractFile) {
                    const contractForm = new FormData();
                    contractForm.append("contract_image", contractFile);

                    return fetch(`/employees/${id}/upload-contract/`, {
                        method: "POST",
                        credentials: "include",
                        body: contractForm
                    });
                }
            })
            .then(() => {
                alert("تم تحديث الموظف بنجاح");
                clearForm();
            })
            .catch(error => {
                console.error('Error during employee update or image upload:', error);
                alert("حدث خطأ أثناء التحديث");
            });
    });





    // Delete
    document.getElementById('delete-btn').addEventListener("click", function () {
        const id = document.getElementById("employee_id").value;
        if (!id) {
            alert("اختر موظفًا أولاً");
            return;
        }

        if (confirm(` هل تريد حذف الموظف رقم ${id}؟`)) {
            customFetch(`/api/employees-api/${id}/`, {
                method: "DELETE"
            })
                .then(() => {
                    alert("employee was deleted successfully");
                    clearForm();
                });
        }
    });

    // Clear selection
    document.getElementById("clear-btn").addEventListener("click", function () {
        clearForm();
    });
    function fetchEmployeeData(employeeId) {
        // API URL for fetching employee data by ID
        const url = `http://45.13.59.226/api/employees-api/${employeeId}/`;

        // Make a GET request to the API
        customFetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch employee data');
                }
                return response.json();
            })
            .then(data => {
                // Populate the form with the fetched data
                document.getElementById("name").value = data.name || '';
                document.getElementById("employee_id").value = data.employee_id || '';
                document.getElementById("nationality").value = data.nationality || '';
                document.getElementById("identity_doc").value = data.identity_doc || '';
                document.getElementById("address").value = data.address || '';
                document.getElementById("phone").value = data.phone || '';
                document.getElementById("salary").value = data.salary || '';
                document.getElementById("last_transaction").value = data.last_transaction || '';
                document.getElementById("start_date").value = data.start_date || '';
                document.getElementById("end_date").value = data.end_date || '';
                document.getElementById("type").value = data.type || ''; // Default to 'Shop_employee' if not set

                // Handle contract image (if exists)
                if (data.contract_image) {
                    // If the image is available, set it to an image element or handle as needed
                    document.getElementById("contract_image").value = data.contract_image;
                } else {
                    document.getElementById("contract_image").value = '';
                }
            })
            .catch(error => {
                console.error('Error fetching employee data:', error);
            });
    }
    employees_table.on("rowClick", function (e, row) {
        console.log("Row clicked after data update:", row.getData());
        const employee_id = row.getData().employee_id; // Get pno of the clicked row
        console.log("Clicked employee_id:", employee_id);

        fetchEmployeeData(employee_id);
    });
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
});
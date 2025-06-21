document.addEventListener("DOMContentLoaded", function () {
    // Initialize Tabulator
    const table = new Tabulator("#tabulator-table", {
        height: "400px",
        layout: "fitColumns",
        placeholder: "لا توجد بيانات متاحة",
        langs: {
            "ar": {
                "pagination": {
                    "first": "الأول",
                    "first_title": "الصفحة الأولى",
                    "last": "الأخير",
                    "last_title": "الصفحة الأخيرة",
                    "prev": "السابق",
                    "prev_title": "الصفحة السابقة",
                    "next": "التالى",
                    "next_title": "الصفحة التالية",
                }
            }
        },
        locale: "ar",
        layoutLocale: true,
        columnHeaderVertAlign: "bottom",
    });

    // Elements
    const fileInput = document.getElementById("fileInput");
    const uploadBtn = document.getElementById("uploadBtn");
    const importBtn = document.getElementById("importBtn");
    const closeBtn = document.getElementById("closeBtn");
    const downloadTemplate = document.getElementById("download-template");
    const importResponseDiv = document.getElementById("import-response");
    const tableSection = document.getElementById("table-section");

    // Upload Excel file
    uploadBtn.addEventListener("click", (event) => {
        event.preventDefault();
        const file = fileInput.files[0];

        if (!file) {
            showAlert("الرجاء اختيار ملف إكسل", "danger");
            return;
        }

        // Show loading state
        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> جاري التحميل...';

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const data = new Uint8Array(e.target.result);
                const workbook = XLSX.read(data, { type: "array" });
                const sheetName = workbook.SheetNames[0];
                const sheet = workbook.Sheets[sheetName];
                const jsonData = XLSX.utils.sheet_to_json(sheet);

                if (jsonData.length > 0) {
                    // Process headers to maintain Arabic names
                    const headers = Object.keys(jsonData[0]).map(header => {
                        // You can add header mapping here if needed
                        return header;
                    });

                    table.setColumns(
                        headers.map((header) => ({
                            title: header,
                            field: header,
                            headerTooltip: header,
                            hozAlign: "right",
                            headerHozAlign: "right"
                        }))
                    );

                    table.setData(jsonData);
                    tableSection.style.display = "block";
                    showAlert("تم تحميل البيانات بنجاح", "success");
                } else {
                    showAlert("لا توجد بيانات في ملف الإكسل", "warning");
                }
            } catch (error) {
                console.error("Error processing file:", error);
                showAlert("حدث خطأ أثناء معالجة الملف", "danger");
            } finally {
                uploadBtn.disabled = false;
                uploadBtn.textContent = "تحميل الملف";
            }
        };

        reader.onerror = () => {
            showAlert("حدث خطأ أثناء قراءة الملف", "danger");
            uploadBtn.disabled = false;
            uploadBtn.textContent = "تحميل الملف";
        };

        reader.readAsArrayBuffer(file);
    });

    // Import data to server
    importBtn.addEventListener("click", (event) => {
        event.preventDefault();
        const data = table.getData();

        if (data.length === 0) {
            showAlert("لا توجد بيانات للاستيراد", "warning");
            return;
        }

        // Show loading state
        importBtn.disabled = true;
        importBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> جاري الاستيراد...';

        importResponseDiv.innerHTML = "";
        importResponseDiv.style.display = "none";

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const formData = new FormData();
        formData.append("csrfmiddlewaretoken", csrfToken);
        formData.append("data", JSON.stringify(data));

        fetch("/import-tabulator-data/", {
            method: "POST",
            body: formData,
        })
            .then(handleResponse)
            .then((result) => {
                importResponseDiv.style.display = "block";

                if (result.status === "success") {
                    showAlert(result.message, "success", importResponseDiv);

                    if (result.results && result.results.length) {
                        renderResultsTable(result.results);
                    }
                } else {
                    showAlert(`خطأ: ${result.message}`, "danger", importResponseDiv);
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                showAlert(`حدث خطأ أثناء الاستيراد: ${error.message}`, "danger", importResponseDiv);
            })
            .finally(() => {
                importBtn.disabled = false;
                importBtn.textContent = "استيراد البيانات";
            });
    });

    // Close/Clear table
    closeBtn.addEventListener("click", () => {
        table.clearData();
        tableSection.style.display = "none";
        fileInput.value = "";
        importResponseDiv.innerHTML = "";
        importResponseDiv.style.display = "none";
        showAlert("تم مسح البيانات", "info");
    });

    // Download template
    downloadTemplate.addEventListener("click", function () {
        const fileUrl = this.getAttribute("data-file-url");
        showAlert("جاري تنزيل الملف النموذج...", "info");

        const link = document.createElement("a");
        link.href = fileUrl;
        link.download = "نموذج_استيراد_المنتجات.xlsx";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });

    // Helper functions
    function showAlert(message, type, element = null) {
        const target = element || document.body;
        const alertDiv = document.createElement("div");
        alertDiv.className = `alert alert-${type} alert-dismissible fade show mt-3`;
        alertDiv.setAttribute("role", "alert");
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        if (!element) {
            // Position at top of page if no specific element
            alertDiv.style.position = "fixed";
            alertDiv.style.top = "20px";
            alertDiv.style.left = "50%";
            alertDiv.style.transform = "translateX(-50%)";
            alertDiv.style.zIndex = "1000";
            alertDiv.style.width = "auto";
            alertDiv.style.maxWidth = "90%";
            document.body.appendChild(alertDiv);

            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alertDiv);
                bsAlert.close();
            }, 5000);
        } else {
            element.prepend(alertDiv);
        }
    }

    function handleResponse(response) {
        if (!response.ok) {
            return response.text().then(text => {
                throw new Error(text || `HTTP error! Status: ${response.status}`);
            });
        }
        return response.json();
    }

    function renderResultsTable(results) {
        let html = `
        <div class="table-responsive mt-3">
            <table class="table table-bordered table-hover">
                <thead class="table-light">
                    <tr>
                        <th>الرقم الخاص</th>
                        <th>اسم الصنف</th>
                        <th>اسم الشركة</th>
                        <th>رقم الشركة</th>
                        <th>الرصيد</th>
                        <th>سعر البيع</th>
                        <th>سعر التوريد</th>
                        <th>سعر التكلفة</th>
                        <th>سعر الشراء</th>
                        <th>اقل سعر للبيع</th>
                        <th>حالة الصنف</th>
                        <th>الحالة</th>
                        <th>الخطأ (إن وجد)</th>
                    </tr>
                </thead>
                <tbody>`;

        results.forEach((r) => {
            html += `
                <tr>
                    <td>${r["الرقم الخاص"] ?? "-"}</td>
                    <td>${r["اسم الصنف"] ?? "-"}</td>
                    <td>${r["اسم الشركة"] ?? "-"}</td>
                    <td>${r["رقم الشركة"] ?? "-"}</td>
                    <td>${r["الرصيد"] ?? "-"}</td>
                    <td>${r["سعر البيع"] ?? "-"}</td>
                    <td>${r["سعر التوريد"] ?? "-"}</td>
                    <td>${r["سعر التكلفة"] ?? "-"}</td>
                    <td>${r["سعر الشراء"] ?? "-"}</td>
                    <td>${r["اقل سعر للبيع"] ?? "-"}</td>
                    <td>${r["حالة الصنف"] ?? "-"}</td>
                    <td class="${r.status === "success" ? "text-success" : "text-danger"}">
                        ${r.status === "success" ? "نجاح" : "فشل"}
                    </td>
                    <td>${r.error ? r.error : "-"}</td>
                </tr>`;
        });

        html += `</tbody></table></div>`;
        importResponseDiv.innerHTML += html;
    }
});
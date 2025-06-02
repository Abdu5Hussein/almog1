document.addEventListener("DOMContentLoaded", function () {

    const table = new Tabulator("#tabulator-table", {
        height: "400px",
        layout: "fitColumns",
        placeholder: "No Data Available",
        rowFormatter: function (row) {
            const existsValue = row.getData().exists; // Get the 'exists' value for the current row
            if (existsValue === 0) {
                row.getElement().style.backgroundColor = "yellow"; // Set the background color to yellow
            } else {
                row.getElement().style.backgroundColor = ""; // Reset the background color if exists is not 0
            }
        },
    });

    document
        .getElementById("uploadBtn")
        .addEventListener("click", (event) => {
            event.preventDefault();
            const fileInput = document.getElementById("fileInput");
            const file = fileInput.files[0];

            if (!file) {
                alert("Please select an Excel file.");
                return;
            }

            const reader = new FileReader();
            reader.onload = (e) => {
                const data = new Uint8Array(e.target.result);
                const workbook = XLSX.read(data, { type: "array" });
                const sheetName = workbook.SheetNames[0];
                const sheet = workbook.Sheets[sheetName];
                const jsonData = XLSX.utils.sheet_to_json(sheet);
                console.log(jsonData);

                if (jsonData.length > 0) {
                    const headers = Object.keys(jsonData[0]);

                    // Send data to backend for item existence check
                    customFetch("/check_items", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken": "{{ csrf_token }}", // Add CSRF token for security
                        },
                        body: JSON.stringify(jsonData), // Send JSON data
                    })
                        .then((response) => {
                            if (!response.ok) {
                                throw new Error(
                                    `HTTP error! Status: ${response.status} error: ${response.message}`
                                );
                            }
                            return response.json();
                        })
                        .then((result) => {
                            if (result.status === "success") {
                                const itemResults = result.results;
                                console.log(itemResults);

                                // Append 'exists' column to jsonData
                                jsonData.forEach((item) => {
                                    const match = itemResults.find(
                                        (res) => res.company_no === item["رقم الشركة"]
                                    );
                                    item.exists = match ? match.exists : 0; // Add 'exists' field
                                    console.log("item.exists", item.exists);
                                });

                                // Dynamically map headers to Tabulator columns
                                const columns = headers.map((header) => {
                                    // Check if the column is "التاريخ" and apply a mutator
                                    if (header === "التاريخ") {
                                        return {
                                            title: header,
                                            field: header,
                                            mutator: function (value) {
                                                // Convert Excel serial date to normal date
                                                let date = new Date(1900, 0, value); // 1900-01-01 + (serialDate)
                                                return date.toISOString().split("T")[0]; // Format as YYYY-MM-DD
                                            },
                                        };
                                    }
                                    return { title: header, field: header }; // Default column
                                });

                                // Add the 'exists' column
                                columns.push({
                                    title: "Exists",
                                    field: "exists",
                                    formatter: function (cell) {
                                        // Return 1 or 0 as a string
                                        return cell.getValue() === 1 ? "1" : "0";
                                    },
                                });

                                // Set columns and data in Tabulator
                                table.setColumns(columns);
                                table.setData(jsonData);
                                refresh_total();
                            } else {
                                alert("Error checking item existence: " + result.message);
                            }
                        })
                        .catch((error) => {
                            console.error("Error:", error);
                            alert("An error occurred while validating items.");
                        });
                } else {
                    alert("No data found in the Excel file.");
                }
            };
            reader.readAsArrayBuffer(file);
        });

    document
        .getElementById("importBtn")
        .addEventListener("click", (event) => {
            event.preventDefault();

            const data = table.getData();

            if (data.length === 0) {
                alert("No data to import.");
                return;
            }

            // Retrieve the table's headers dynamically from the first row of data
            const headers = Object.keys(data[0]);

            // Specify the required columns as an array
            const requiredColumns = ["الكمية", "اسم الصنف"]; // Add more column names as needed

            // Check if all required columns exist in the data
            const missingColumns = requiredColumns.filter(
                (col) => !headers.includes(col)
            );

            if (missingColumns.length > 0) {
                alert(
                    `حدث خطأ, لا يوجد في البيانات الأعمدة المطلوبة التالية: (${missingColumns.join(", ")})`
                );
                return null; // Exit the function and return null
            }

            // Retrieve the value of the invoice input field
            const invoiceInput = document.getElementById("invoice");
            const invoiceNo = invoiceInput ? invoiceInput.value : null;

            if (!invoiceNo) {
                alert("Invoice number is required.");
                return;
            }

            const formData = new FormData();
            formData.append("csrfmiddlewaretoken", "{{ csrf_token }}"); // Add CSRF token
            formData.append("data", JSON.stringify(data)); // Add the data to be imported
            formData.append("invoice_no", invoiceNo); // Add the invoice number

            console.log("Sending data to the server:", formData);
            console.log("invoice:", invoiceNo);
            console.log("table data:", JSON.stringify(data));

            customFetch("/process_buyInvoice_excel", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": "{{ csrf_token }}", // CSRF token for security
                },
                body: JSON.stringify({
                    data: JSON.stringify(data), // Stringify the data as expected by the server
                    invoice_no: invoiceNo, // Include invoice number
                }), // Send the stringified data and invoice number
            })
                .then((response) => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    return response.json();
                })
                .then((result) => {
                    console.log("Response from server:", result);
                    if (result.status === "success") {
                        alert(result.message);
                    } else {
                        alert("Error: " + result.message);
                    }
                })
                .catch((error) => {
                    console.error("Error:", error);
                    alert("An error occurred while importing data.");
                });
        });

    document.getElementById("closeBtn").addEventListener("click", () => {
        window.close();
    });

    function calculateColumnSum(columnName) {
        let sum = 0;
        const rowData = table.getData(); // Fetch row data from Tabulator

        if (Array.isArray(rowData)) {
            // Ensure rowData is an array
            rowData.forEach((row) => {
                if (!isNaN(row[columnName])) {
                    sum += parseFloat(row[columnName]); // Convert to float and add to sum
                }
            });
        } else {
            console.error(
                `rowData is not an array or is undefined for column: ${columnName}`
            );
        }

        return parseFloat(sum);
    }
    refresh_total();
    function refresh_total() {
        const total = calculateColumnSum("سعر الشراء");
        document.getElementById("order-total").value = total;
    }
});
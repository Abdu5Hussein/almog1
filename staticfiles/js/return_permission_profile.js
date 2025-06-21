document.addEventListener("DOMContentLoaded", function () {
    var table = new Tabulator("#return-table", {
        data: [], // Assign the data to the table
        layout: "fitColumns", // Adjust column widths to fit data
        columns: [
            { title: "رقم خاص", field: "pno" },
            { title: "رقم الشركة", field: "company_no" },
            { title: "اسم الشركة", field: "company" },
            { title: "الصنف", field: "item_name" },
            { title: "كمية الفاتورة", field: "org_quantity", hozAlign: "right" },
            { title: "الكمية المرجعة", field: "returned_quantity", hozAlign: "right" },
            { title: "سعر القطعة", field: "price", hozAlign: "right", formatter: "money" },
            { title: "الاجمالي", field: "total", hozAlign: "right", formatter: "money" },
            { title: "رقم الفاتورة", field: "invoice_no" }
        ],
        movableColumns: true, // Allow columns to be moved
        resizableRows: true,  // Allow rows to be resized
        pagination: true,     // Enable pagination
        paginationSize: 5,   // Set number of rows per page
    });
    const urlParams = new URLSearchParams(window.location.search);
    const buyReturn = urlParams.get('buy_return');

    function setInputValue(id, value) {
        document.getElementById(id).value = value;
    }

    function addPermissionItems(permission) {
        let url;
        if (buyReturn) {
            url = "/buy-invoice/" + invoice_no + "/" + permission + "/return-items/?buy_return=1";
        } else {
            url = "/sell-invoice/" + invoice_no + "/" + permission + "/return-items/";
        }
        invoice_no = document.getElementById("return-invoice-no").value;
        openWindow(url);
    }
    function fetchData() {
        /* // Fetch data from the API endpoint
        let url;
        if (buyReturn) {
            url = "/api/buy-permissions/";
        } else {
            url = "/permissions/";
        }
        customFetch(url)
            .then(response => response.json()) // Parse JSON data from response
            .then(data => {
                // Initialize Tabulator with the fetched data
                console.log(data);
                table.setData(data.results);

            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });*/
    }
    //fetchData();
    refresh_table_items()
    document.getElementById('returnButton').addEventListener('click', function () {
        const permission = document.getElementById("return-autoid").value;
        addPermissionItems(permission);
    });
    document.getElementById('refresh-btn').addEventListener('click', function () {
        refresh_table_items();
    });
    function refresh_table_items() {
        const invoice = document.getElementById("return-invoice-no").value

        if (invoice) {
            fetchInvoiceItems(invoice);
        }
    }


    const today = new Date();
    const formattedDate = today.toISOString().split("T")[0]; // Format date as YYYY-MM-DD
    document.getElementById("return-date").value = formattedDate;
    let childWindows = [];
    function openWindow(url, width = 600, height = 700) {
        // Get the parent window's dimensions and position
        const parentWidth = window.innerWidth;
        const parentHeight = window.innerHeight;
        const parentLeft = window.screenX;
        const parentTop = window.screenY;

        // Calculate the center position for the child window
        const left = parentLeft + (parentWidth - width) / 2;
        const top = parentTop + (parentHeight - height) / 2;

        // Open a new child window
        const childWindow = window.open(
            url,
            "_blank",
            `width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=yes`
        );

        if (!childWindow) {
            alert("Pop-up blocked! Please allow pop-ups for this website.");
            return;
        }

        /* // Set the child window's size and disable resizing by enforcing it every time it's resized
                      childWindow.addEventListener('resize', () => {
                        // Enforce fixed size by resetting the size after any resize attempt
                        childWindow.resizeTo(width, height);
                      });*/

        // Add the new child window to the array
        childWindows.push(childWindow);

        // Monitor the child window's state
        const monitorChild = setInterval(() => {
            if (childWindow.closed) {
                // Remove the closed window from the array
                childWindows = childWindows.filter((win) => win !== childWindow);
                clearInterval(monitorChild);
            }
        }, 300);

        /*// Focus all child windows periodically
                      setInterval(() => {
                        childWindows.forEach(win => {
                          if (!win.closed) {
                            win.focus();
                          }
                        });
                      }, 500);*/

        // Close all child windows when the parent is closed
        window.onbeforeunload = function () {
            childWindows.forEach((win) => {
                if (!win.closed) {
                    win.close();
                }
            });
        };
    }
    async function fetchInvoiceItems(invoiceId) {
        let url;
        if (buyReturn) {
            url = `/buy-invoice/${invoiceId}/returned-items?buy_return=1`;
        } else {
            url = `/sell-invoice/${invoiceId}/returned-items`;
        }

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
            table.setData(data.data);
            setInputValue("returned", calculateColumnSum("total") + " دل ");
            setInputValue("quantity", calculateColumnSum("returned_quantity"));
            setInputValue("total", data.invoice_total + " دل ");
            setInputValue("paid", data.invoice_paid + " دل ");
            const remaining = parseFloat(data.invoice_total) - parseFloat(data.invoice_paid);
            setInputValue("remaining", remaining + " دل ");
            return data; // Return the fetched data
        } catch (error) {
            console.error("Error fetching invoice items:", error.message);
            alert("! حدث خطا اثناء جلب الاصناف المرجعة !");
            return null; // You can handle errors differently, e.g., show a user-friendly message
        }
    }
    /*function get_invoice_returned_items() {
      const invoice = parseFloat(
        document.getElementById("invoice-autoid").value.trim()
      );
      console.log("invioce", invoice);

      fetchInvoiceItems(invoice).then((items) => {
        if (items) {
          console.log("Invoice items:", items);
          table.replaceData(items); // Add the row data to second_table
          let totalPrice = calculateColumnSum("dinar_total_price"); // Get the column sum
          let totalcost = isNaN(calculateColumnSum("cost_total_price")) ? 0 : calculateColumnSum("cost_total_price");
          let netcost = totalcost==0 ? 0 : totalcost - totalPrice;
          let roundedPrice = parseFloat(totalPrice).toFixed(2);
          document.getElementById("total").value = roundedPrice + " دل ";
          document.getElementById("expenses").value =  parseFloat(netcost).toFixed(2) + " دل";
          document.getElementById("org-price").value =
            calculateColumnSum("org_total_price").toFixed(2);
           let netTotal = totalPrice + netcost;
          document.getElementById("net-total").value = parseFloat(netTotal).toFixed(2) + " دل ";
          const paidValue = parseFloat(document.getElementById("paid").value);
          let remainingValue = isNaN(paidValue)? netTotal: netTotal - paidValue;
          document.getElementById("remaining").value = parseFloat(remainingValue).toFixed(2) + " دل ";
          // Handle the fetched items, e.g., display them in the UI
        } else {
          console.log("No items fetched or an error occurred.");
          table.replaceData([]);
        }
      });
    }*/
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
    document.getElementById("print-btn").addEventListener("click", () => {
        const data = {
            label: "specific_return_permission",
            invoice_no: document.getElementById("return-autoid").value,
        };

        customFetch(`/api/print-dynamic-paper`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()  // <-- IMPORTANT for Django
            },
            body: JSON.stringify(data),
        })
            .then(response => response.text())  // <-- handle HTML or plain text
            .then(html => {
                const printWindow = window.open("", "_blank");
                printWindow.document.open();
                printWindow.document.write(html);
                printWindow.document.close();
            })
            .catch((error) => {
                console.error("Error fetching data:", error);
            });
    });
});
document.addEventListener('DOMContentLoaded', () => {
    function disableInput(input) {
        const inputbtn = document.getElementById(input);
        inputbtn.disabled = true;
    }

    function checkStatus(status) {
        //const validated_btn = document.getElementById("reviewer-section");
        //const inProgress_btn = document.getElementById("");

        switch (status) {
            case "لم تحضر": break;
            case "جاري التحضير":
                disableInput("inProgress_btn");
                disableInput("preparedBy");
                disableInput("note");
                break;
            case "روجعت":
            case "سلمت جزئيا":
                disableInput("validated_btn");
                disableInput("preparedBy");
                disableInput("note");
                disableInput("box-size");
                disableInput("place");
                disableInput("reviewer-name");
                disableInput("inProgress_btn");
                break;
            case "سلمت":
                disableInput("validated_btn");
                disableInput("preparedBy");
                disableInput("note");
                disableInput("box-size");
                disableInput("place");
                disableInput("reviewer-name");
                disableInput("inProgress_btn");

                disableInput("biller");
                disableInput("preparer");
                disableInput("reviewer");
                disableInput("deliverer");
                disableInput("box-size2");
                disableInput("sent_by");
                disableInput("office");
                disableInput("delivered_date");
                disableInput("bill");
                disableInput("deliverer-name");

                break;
        }
    }
    const contextData = window.contextData;

    // Now you can use the contextData in your JS logic
    console.log("contextData: ", contextData);  // Output: value
    checkStatus(contextData.invoice_status);

    function inProgress_func() {
        const name = document.getElementById("preparedBy").value;
        const note = document.getElementById("note").value;
        const data = {
            name: name,
            note: note,
            invoice_id: contextData.invoice_no,
        }
        console.log(data);

        customFetch(`prepare_sell_invoice`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        })
            .then((response) => response.json())
            .then((result) => {
                console.log(result);
                alert("جاري تحضير الفاتورة");
            })
            .catch((error) => {
                console.error("Error:", error);
            }).finally(() => {
                location.reload();
            });
    }
    const inProgress_btn = document.getElementById("inProgress_btn");
    inProgress_btn.addEventListener("click", function () {
        inProgress_func();
    })

    function validated_func() {
        const inProgress_btn = document.getElementById("inProgress_btn").disabled;

        if (!inProgress_btn) {
            alert("! الفاتورة لم تحضر بعد !");
            return;
        }

        const reviewer = document.getElementById("reviewer-name").value;
        const place = document.getElementById("place").value;
        const size = document.getElementById("box-size").value;
        const invoice_no = document.getElementById("invoice-no").value;
        const note = document.getElementById("final-note").value;

        const data = {
            reviewer: reviewer,
            place: place,
            size: size,
            invoice_id: invoice_no,
            final_note: note,
        }
        console.log(data);

        customFetch(`validate_sell_invoice`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        })
            .then((response) => response.json())
            .then((result) => {
                console.log(result);
                alert("تم مراجعة الفاتورة");
            })
            .catch((error) => {
                console.error("Error:", error);
            }).finally(() => {
                location.reload();
            });
    }
    function deliverInvoice_func(status) {
        const biller = document.getElementById("biller").value;
        const size = document.getElementById("box-size2").value;
        const sent = document.getElementById("sent_by").value;
        const office = document.getElementById("office").value;
        const bill = document.getElementById("bill").value;
        const deliverer = document.getElementById("deliverer").value;
        const deliverer_date = document.getElementById("delivered_date").value;
        const invoice_no = document.getElementById("invoice-no").value;
        const note = document.getElementById("final-note").value;

        const validated_btn = document.getElementById("validated_btn").disabled;

        if (!validated_btn) {
            alert("! الفاتورة لم تراجع بعد !");
            return;
        }

        const data = {
            biller: biller,
            size: size,
            office: office,
            sent: sent,
            bill: bill,
            deliverer: deliverer,
            deliverer_date: deliverer_date,
            status: status,
            final_note: note,
            invoice_id: invoice_no,
        }
        console.log(data);

        customFetch(`deliver_sell_invoice`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        })
            .then((response) => response.json())
            .then((result) => {
                console.log(result);
                alert("تم تسليم الفاتورة");
            })
            .catch((error) => {
                console.error("Error:", error);
            }).finally(() => {
                //location.reload();
            });
    }

    const reviewer = document.getElementById("reviewer-name");
    reviewer.addEventListener("change", function () {
        document.getElementById("reviewer").value = this.value;
    })

    const Done_btn = document.getElementById("Done_btn");
    Done_btn.addEventListener("click", function () {
        deliverInvoice_func("سلمت");
    })

    const partly_btn = document.getElementById("partly_btn");
    partly_btn.addEventListener("click", function () {
        deliverInvoice_func("سلمت جزئيا");
    })
    const validated_btn = document.getElementById("validated_btn");
    validated_btn.addEventListener("click", function () {
        validated_func();
    })

    const preparedBy = document.getElementById("preparedBy");
    preparedBy.addEventListener("change", function () {
        document.getElementById("preparer").value = this.value;
    })
    const deliverer = document.getElementById("deliverer");
    deliverer.addEventListener("change", function () {
        document.getElementById("deliverer-name").value = this.value;
    })
    function cancel_func() {
        const invoice_no = document.getElementById("invoice-no").value;


        const data = {
            invoice_id: invoice_no,
        }
        console.log(data);

        customFetch(`cancel_sell_invoice`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        })
            .then((response) => response.json())
            .then((result) => {
                console.log(result);
                alert("تم الغاء الفاتورة");
            })
            .catch((error) => {
                console.error("Error:", error);
            }).finally(() => {
                location.reload();
            });

    }
    const cancel_btn = document.getElementById("cancel_btn");
    cancel_btn.addEventListener("click", function () {
        cancel_func();
    })

    const delivery_btn = document.getElementById("deliver_to_driver");
    delivery_btn.addEventListener("click", function () {
        const id = document.getElementById("invoice-no").value;
        openWindow("/assign-orders-page/" + id + "/");
    })
    //let windows = {}; // Object to keep track of opened windows

    // Function to open a new window or focus an existing one
    function openWindow(url, name, width = 1100, height = 700) {
        // Check if the window is already open
        if (windows[name] && !windows[name].closed) {
            windows[name].focus(); // Bring the existing window to the front
        } else {
            // Get the screen width and height
            const screenWidth = window.innerWidth;
            const screenHeight = window.innerHeight;

            // Calculate the position to center the window
            const left = (screenWidth - width) / 2;
            const top = (screenHeight - height) / 2;

            // Open the window with the specified or default dimensions, centered
            windows[name] = window.open(
                url,
                name,
                `width=${width},height=${height},left=${left},top=${top}`
            );
        }
    }

    const selects = document.querySelectorAll("select");

    selects.forEach((select) => {
        const choices = new Choices(select, {
            searchEnabled: true,
            removeItemButton: true,
            addItems: true,
            addChoices: true,
            duplicateItemsAllowed: false,
        });

        // Optional event listeners
        select.addEventListener("change", (e) => {
            console.log(`Changed value for #${select.id || 'unnamed select'}:`, e.target.value);
        });

        select.addEventListener("choice", (event) => {
            console.log(`Choice selected:`, event.detail.choice);
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const table = new Tabulator("#table", {
        index: "fileid", // Use "fileid" as the unique row identifier
        height: "auto", // Adjust height or set a fixed height
        layout: "fitColumns",
        selectable: true,
        pagination: "local", // Enable local pagination
        paginationSize: 100, // Show 100 records per page
        paginationSizeSelector: [50, 100, 200], // Page size options
        paginationButtonCount: 5, // Number of visible pagination buttons
        movableColumns: true,
        columnHeaderVertAlign: "bottom",
        columnMenu: true, // Enable column menu
        data: [], // Placeholder, will be loaded dynamically
        columns: [
            { title: "رقم الي", field: "autoid", width: 90 },
            { title: "التاريخ", field: "date", width: 90 },
            { title: "البند", field: "cat", width: 90 },
            { title: "سعر التحويل", field: "exchange_rate", width: 90 },
            { title: "قيمة التحويل", field: "amount", width: 90 },

            { title: "القيمة", field: "dinar_amount", width: 90 },
            { title: "مقابل", field: "for", width: 90 },
            { title: "ملاحظات", field: "note", width: 90 },
        ],
        placeholder: "No Data Available",
        rowFormatter: function (row) {
            var rowData = row.getData(); // Get the row data

            // You can add more conditions as needed
        }, // Message when no data is present or after filtering
        rowClick: function (e, row) {
            const clickedPno = row.getData().pno; // Get pno of the clicked row
            console.log("Clicked Pno:", clickedPno);
        },
        tableBuilt: function () {
            console.log("table built");
        },
    });
});
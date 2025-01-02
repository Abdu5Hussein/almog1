
console.log("Script Loaded");

document.addEventListener("DOMContentLoaded", function () {
  const csrfToken = $("meta[name='csrf-token']").attr("content");
  if (csrfToken) {
    console.log("token exist");
  }






  const url = document.getElementById('users-table').getAttribute('data-url');

  let currentPage = 1;
  let pageSize = 500;
  const reqUrl = `${url}?page=${currentPage}&size=${pageSize}`;
  // Use the URL in your fetch request
  /*fetch(url)
    .then((response) => response.json())
    .then((data) => {
      console.log("Fetched Data:", data);
      agTable.api.setRowData(data.data);
    })
    .catch((error) => console.error("Error fetching data:", error));*/

  ////////////////////
  // Initialize Tabulator
  // Define grid options
  const gridOptions = {
    rowData: [],
    columnDefs: [
      // Column definitions for your grid
      { headerName: "الرقم الخاص", field: "pno", width: 100, hide: false },
      { headerName: "الشركة المصنعة", field: "companyproduct", width: 96, hide: false },
      { headerName: "رقم الشركة", field: "replaceno", width: 150, hide: false },
      { headerName: "الرقم الاصلي", field: "itemno", width: 90, hide: false },
      { headerName: "اسم الصنف ع", field: "itemname", width: 280, hide: false },
      { headerName: "الرصيد", field: "itemvalue", width: 81, hide: false },
      { headerName: "سعر البيع", field: "buyprice", width: 75, hide: false },
      { headerName: "الموقع", field: "itemplace", width: 75, hide: false },
      { headerName: "رقم الملف", field: "fileid", hide: true },
      { headerName: "البيان الرئيسي", field: "itemmain", hide: true },
      { headerName: "البيان الفرعي", field: "itemsubmain", hide: true },
      { headerName: "الموديل", field: "itemthird", hide: true },
      { headerName: "بلد الصنع", field: "itemsize", hide: true },
      { headerName: "Date Product", field: "dateproduct", hide: true },
      { headerName: "Level Product", field: "levelproduct", hide: true },
      { headerName: "الرصيد الاحتياطي", field: "itemtemp", hide: true },
      { headerName: "تاريخ اخر طلب", field: "orderlastdate", hide: true },
      { headerName: "مصدر الطلب", field: "ordersource", hide: true },
      { headerName: "رقم فاتورة الطلب", field: "orderbillno", hide: true },
      { headerName: "تاريخ اخر شراء", field: "buylastdate", hide: true },
      { headerName: "مصدر الشراء", field: "buysource", hide: true },
      { headerName: "رقم فاتورة الشراء", field: "buybillno", hide: true },
      { headerName: "سعر التوريد", field: "orgprice", hide: true },
      { headerName: "سعر الشراء", field: "orderprice", hide: true },
      { headerName: "سعر التكلفة", field: "costprice", hide: true },
      { headerName: "المواصفات", field: "memo", hide: true },
      { headerName: "Order Stop", field: "orderstop", hide: true },
      { headerName: "Buy Stop", field: "buystop", hide: true },
      { headerName: "Item Trans", field: "itemtrans", hide: true },
      { headerName: "الرصيد المؤقت", field: "itemvalueb", hide: true },
      { headerName: "Item Type", field: "itemtype", hide: true },
      { headerName: "رقم الباركود", field: "barcodeno", hide: true },
      { headerName: "اسم الصنف بالانجليزي", field: "eitemname", hide: true },
      { headerName: "عملة الشراء", field: "currtype", hide: true },
      { headerName: "اقل سعر", field: "lessprice", hide: true },
      { headerName: "قيمة العملة", field: "currvalue", hide: true },
      { headerName: "الرصيد المحجوز", field: "resvalue", hide: true },
      { headerName: "عدد القطع للصندوق", field: "itemperbox", hide: true },
      { headerName: "حالة الصنف", field: "cstate", hide: true }
    ],
    rowModelType: "infinite",
    cacheBlockSize: 100,
    cacheOverflowSize: 2,
    maxConcurrentDatasourceRequests: 2,
    infiniteInitialRowCount: 1,
    maxBlocksInCache: 2,
    pagination: true,
    paginationAutoPageSize: true,
    paginationPageSizeSelector: [100, 300, 500, 700, 1000], // Page size options
    // Set up remote pagination with the API
    datasource: {
      rowCount: undefined, // behave as infinite scroll
      getRows(params) {
        const page = params.startRow / params.endRow; // Calculate the page index based on rows requested
        const size = params.endRow - params.startRow; // Number of rows requested (page size)
        const reqUrl = `${url}?startRow=${page}&endRow=${size}`;
        console.log(reqUrl);
        console.log("Requesting data from:", reqUrl);

        fetch(url)
          .then((response) => response.json())
          .then((data) => {
            console.log("Fetched Data:", data);
            console.log("params:", params);

            // Provide the grid with the rows
            params.successCallback(data.rows, data.rowCount); // `data.totalCount` should be the total number of rows available in the backend

            // Log the number of rows fetched
            console.log("Number of rows fetched:", data.rows.length);
          })
          .catch((error) => {
            console.error("Error fetching data:", error);

            // Inform the grid of a failure
            params.failCallback();
          });
      },
    },

    // Event handler for row click
    onRowClicked: function (event) {
      console.log('Row clicked', event.node.data);
      // Handle row click
    },

    // Styling rows based on conditions
    getRowStyle: function (params) {
      const {
        itemvalue = '',
        itemvalueb = '',
        buyprice = 0,
        costprice = 0,
        itemtemp = '',
        orgprice = 0,
        orderprice = 0,
      } = params.data || {};

      if (itemvalue <= itemtemp) {
        return { backgroundColor: "#ffffe0" }; // Yellow row
      }
      if (itemvalue === 0 && itemvalueb === 0) {
        return { backgroundColor: "#ffc0c0" }; // Red row
      }
      if (costprice > buyprice) {
        return { backgroundColor: "#ffdab9" }; // Orange row
      }
      if (itemvalueb > 0) {
        return { backgroundColor: "#d8f3dc" }; // Green row
      }
      if (costprice === 0 || orderprice === 0 || orgprice === 0) {
        return { backgroundColor: "red" }; // Red row
      }

      return null;
    }
  };

  // Get the div where the grid will be placed
  const gridDiv = document.querySelector('#users-table');

  // Initialize AG-Grid on the div
  const agTable = new agGrid.createGrid(gridDiv, gridOptions);

  // Handle pagination data (received from the API)
  gridOptions.paginationDataReceived = function (paginationData) {
    console.log("paginationData: ", paginationData);
  };

  //table.options.tableBuilt();

  //////////////////
  // Function to fetch data based on the current page and page size
  agTable.refreshInfiniteCache();
  function setupAgGridWithInfiniteScroll() {
    console.log("triggered");

    const datasource = {
      rowCount: undefined, // behave as infinite scroll
      getRows(params) {
        const page = params.startRow / params.endRow; // Calculate the page index based on rows requested
        const size = params.endRow - params.startRow; // Number of rows requested (page size)
        const reqUrl = `${url}?page=${page}&size=${size}`;
        console.log(reqUrl);
        console.log("Requesting data from:", reqUrl);

        fetch(reqUrl)
          .then((response) => response.json())
          .then((data) => {
            console.log("Fetched Data:", data);

            // Provide the grid with the rows
            params.successCallback(data.data, data.totalCount); // `data.totalCount` should be the total number of rows available in the backend

            // Log the number of rows fetched
            console.log("Number of rows fetched:", data.data.length);
          })
          .catch((error) => {
            console.error("Error fetching data:", error);

            // Inform the grid of a failure
            params.failCallback();
          });
      },
    };

    // Set the datasource to the AG Grid instance
    agTable.setGridOption("datasource", datasource);
    //agTable.setDatasource(datasource);
    console.log("api", agTable.getRenderedNodes());
    console.log("data", datasource);

  }


  //fetchData(currentPage, pageSize);
  //setupAgGridWithInfiniteScroll();

  // Show/Hide dropdown menu on button click
  document.getElementById("toggle-column-menu").addEventListener("click", function () {
    const dropdown = document.getElementById("column-menu");
    dropdown.style.display = dropdown.style.display === "none" || dropdown.style.display === "" ? "block" : "none";
  });

  // Column visibility handlers (attach to checkboxes after table initialization)
  function setupColumnVisibilityHandlers(gridOptions) {
    document.querySelectorAll('#column-menu input[type="checkbox"]').forEach((checkbox) => {
      checkbox.addEventListener("change", function () {
        const columnField = this.value;
        gridOptions.columnApi.setColumnVisible(columnField, this.checked); // Show or hide the column
      });
    });
  }
  /*function defaultColumns(table) {
    // Define the custom object containing the columns to show
    const visibleColumns = {
      fileid: true,   // Specify the columns you want to show
      itemmain: true, // Add more columns as needed
      itemvalue: true,
    };
  
    // Loop through all checkboxes in the column menu
    document.querySelectorAll('#column-menu input[type="checkbox"]').forEach((checkbox) => {
      const columnField = checkbox.value; // Get the field from the checkbox value
  
      // Check if the columnField exists in visibleColumns and its value is true
      if (visibleColumns[columnField]) {
        table.showColumn(columnField); // Show the column
        checkbox.checked = true;      // Update the checkbox state
      } else {
        table.hideColumn(columnField); // Hide the column
        checkbox.checked = false;     // Update the checkbox state
      }
    });
  }*/


  // Column visibility handlers (attach to checkboxes after table initialization)

  ////////////
  /*
    agTable.api.addEventListener("rowSelected", function () {
      const selectedRows = table.getSelectedRows();
      console.log("Selected Rows:", selectedRows); // Log when selection changes
    });*/


  // Prevent default context menu within #users-table div
  $("#users-table").on("contextmenu", function (e) {
    e.preventDefault(); // Prevent default right-click menu on table
  });
  /*
    // Handle right-click on row
    agTable.api.addEventListener("rowContext", function (e, row) {
      e.preventDefault();
      window.currentRow = row; // Save row for later use in performAction
      const contextMenu = document.getElementById("contextMenu");
      contextMenu.style.left = `${e.pageX}px`;
      contextMenu.style.top = `${e.pageY}px`;
      contextMenu.style.display = "block";
    });*/

  // Hide custom context menu when clicking outside
  document.addEventListener("click", function (e) {
    const contextMenu = document.getElementById("contextMenu");
    if (!e.target.closest("#contextMenu") && !e.target.closest("#users-table")) {
      contextMenu.style.display = "none"; // Hide context menu
    }
  });
  /*
    // Perform actions on context menu
    window.performAction = function (action) {
      if (!window.currentRow) return;
  
      const rowData = window.currentRow.getData();
      switch (action) {
        case "Edit":
          alert(`Editing row with ID: ${rowData.fileid}`);
          break;
        case "Delete":
          alert(`Deleting row with ID: ${rowData.fileid}`);
          break;
        case "View Details":
          alert(`Viewing details for row with ID: ${rowData.fileid}`);
          break;
        default:
          console.log("Action not recognized");
      }
      document.getElementById("contextMenu").style.display = "none"; // Hide context menu after action
    };*/


  // Function to get CSRF token
  function getCSRFToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]").value;
  }
  function createNewRecord() {
    // Get selected country, skip if index is 0 (reset value)
    const countrySelect = document.getElementById("countries");
    const selectedCountryName = countrySelect.selectedIndex !== 0 ? countrySelect.options[countrySelect.selectedIndex].text : "";

    // Get selected item-main, skip if index is 0 (reset value)
    const itemMainSelect = document.getElementById("item-main");
    const selectedItemMainText = itemMainSelect.selectedIndex !== 0 ? itemMainSelect.options[itemMainSelect.selectedIndex].text : "";

    // Get selected item-sub-main, skip if index is 0 (reset value)
    const itemSubMainSelect = document.getElementById("item-sub-main");
    const selectedItemSubMainText = itemSubMainSelect.selectedIndex !== 0 ? itemSubMainSelect.options[itemSubMainSelect.selectedIndex].text : "";

    // Get selected company, skip if index is 0 (reset value)
    const companySelect = document.getElementById("company");
    const selectedCompanyText = companySelect.selectedIndex !== 0 ? companySelect.options[companySelect.selectedIndex].text : "";

    // Get selected company, skip if index is 0 (reset value)
    const modelSelect = document.getElementById("model");
    const selectedModelText = modelSelect.selectedIndex !== 0 ? modelSelect.options[modelSelect.selectedIndex].text : "";

    // Data object with correct CSRF token retrieval
    const data = {
      csrfmiddlewaretoken: getCSRFToken(),
      originalno: document.getElementById("original-no")?.value || "",
      itemmain: selectedItemMainText,
      itemsub: selectedItemSubMainText,
      pnamearabic: document.getElementById("pname-arabic")?.value || "",
      pnameenglish: document.getElementById("pname-english")?.value || "",
      company: selectedCompanyText,
      companyno: document.getElementById("company-no")?.value || "",
      pno: document.getElementById("pno")?.value || "",
      barcode: document.getElementById("barcode-no")?.value || "",
      description: document.getElementById("description")?.value || "",
      country: selectedCountryName,
      pieces4box: document.getElementById("pieces-per-box")?.value || 0,
      model: selectedModelText || "",
      storage: document.getElementById("storage-balance")?.value || 0,
      backup: document.getElementById("backup-balance")?.value || 0,
      temp: document.getElementById("temp-balance")?.value || 0,
      reserved: document.getElementById("reserved-balance")?.value || 0,
      location: document.getElementById("location")?.value || "",
      originprice: document.getElementById("origin-price")?.value || 0,
      buyprice: document.getElementById("buy-price")?.value || 0,
      expensesprice: document.getElementById("expenses-price")?.value || 0,
      sellprice: document.getElementById("sell-price")?.value || 0,
      lessprice: document.getElementById("less-price")?.value || 0,
    };

    fetch("/create_main_item/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(), // Add the CSRF token here
      },
      body: JSON.stringify(data),
    })
      .then((response) => {
        if (response.ok) {
          alert("Record created successfully!");

          // Refresh the AG Grid datasource to reflect the new data
          agTable.api.refreshInfiniteCache(); // Reloads data dynamically from the datasource
        } else {
          alert("Error creating record.");
          console.log(getCSRFToken()); // Check the value of the CSRF token
        }
      })
      .catch((error) => console.error("Error:", error));

  }
  ////edit function
  document.getElementById("editButton").addEventListener("click", function (event) {
    event.preventDefault();  // Prevent form submission

    // Get selected country, skip if index is 0 (reset value)
    const countrySelect = document.getElementById("countries");
    const selectedCountryName = countrySelect.selectedIndex !== 0 ? countrySelect.options[countrySelect.selectedIndex].text : "";

    // Get selected item-main, skip if index is 0 (reset value)
    const itemMainSelect = document.getElementById("item-main");
    const selectedItemMainText = itemMainSelect.selectedIndex !== 0 ? itemMainSelect.options[itemMainSelect.selectedIndex].text : "";

    // Get selected item-sub-main, skip if index is 0 (reset value)
    const itemSubMainSelect = document.getElementById("item-sub-main");
    const selectedItemSubMainText = itemSubMainSelect.selectedIndex !== 0 ? itemSubMainSelect.options[itemSubMainSelect.selectedIndex].text : "";

    // Get selected company, skip if index is 0 (reset value)
    const companySelect = document.getElementById("company");
    const selectedCompanyText = companySelect.selectedIndex !== 0 ? companySelect.options[companySelect.selectedIndex].text : "";

    // Get selected company, skip if index is 0 (reset value)
    const modelSelect = document.getElementById("model");
    const selectedModelText = modelSelect.selectedIndex !== 0 ? modelSelect.options[modelSelect.selectedIndex].text : "";

    // Assuming window.currentRow holds the selected row that needs to be edited
    if (window.currentRow) {
      // Get the data from the form fields
      const data = {
        csrfmiddlewaretoken: getCSRFToken(), // CSRF token for security
        fileid: window.currentRow.data.fileid, // Use fileid or primary key to identify the record
        originalno: document.getElementById("original-no").value || "",
        itemmain: selectedItemMainText, // Use the inner text (item-main)
        itemsub: selectedItemSubMainText, // Use the inner text (item-sub-main)
        pnamearabic: document.getElementById("pname-arabic").value || "",
        pnameenglish: document.getElementById("pname-english").value || "",
        company: selectedCompanyText, // Use the inner text (company)
        companyno: document.getElementById("company-no").value || "",
        pno: document.getElementById("pno").value || "",
        barcode: document.getElementById("barcode-no").value || "",
        description: document.getElementById("description").value || "",
        country: selectedCountryName, // Use the inner text (country name)
        pieces4box: document.getElementById("pieces-per-box").value || 0,
        model: selectedModelText || "",
        storage: document.getElementById("storage-balance").value || 0,
        backup: document.getElementById("backup-balance").value || 0,
        temp: document.getElementById("temp-balance").value || 0,
        reserved: document.getElementById("reserved-balance").value || 0,
        location: document.getElementById("location").value || "",
        originprice: document.getElementById("origin-price").value || 0,
        buyprice: document.getElementById("buy-price").value || 0,
        expensesprice: document.getElementById("expenses-price").value || 0,
        sellprice: document.getElementById("sell-price").value || 0,
        lessprice: document.getElementById("less-price").value || 0,
      };

      // Send the data to the server via a PUT or PATCH request
      fetch("/edit_main_item/", {
        method: "PATCH",  // Use PATCH for partial update or PUT for full update
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(), // CSRF token for security
        },
        body: JSON.stringify(data), // Send the data as JSON
      })
        .then((response) => {
          if (response.ok) {
            alert("Record updated successfully!");

            /*// Option 1: Update the row directly in AG Grid
            const updatedRowData = { ...rowData, ...data }; // Merge new data with old data
            agTable.api.applyTransaction({ update: [updatedRowData] }); // Update the row in AG Grid*/

            // Option 2: Refresh data from the server (if needed)
            agTable.api.refreshInfiniteCache(); // For infinite row model
          } else {
            alert("Error updating record.");
          }
        })
        .catch((error) => console.error("Error:", error));
    } else {
      alert("من فضلك اختر سطرًا لتعديله.");
    }
  });

  document.getElementById("oem-btn").addEventListener("click", function (event) {
    // Retrieve `sessionStorage` data
    const companyName = sessionStorage.getItem('company-name');
    const companyNo = sessionStorage.getItem('company-no');

    if (companyName && companyNo) {
      // Construct the URL with query parameters
      const url = `/oem?company_name=${encodeURIComponent(companyName)}&company_no=${encodeURIComponent(companyNo)}`;

      // Open a new window with the constructed URL
      openWindow(url);
    } else {
      alert("يرجى اختيار عنصر");
      console.error('Missing sessionStorage values');
    }

  });
  //show model select items for selected maintype
  // Get the select elements
  const modelSelect = document.getElementById("model");
  const mainTypeSelect = document.getElementById("item-main");

  // Event listener for mainType select change
  mainTypeSelect.addEventListener("change", function () {
    const selectedMainType = mainTypeSelect.value;

    // Loop through all model options and hide those that don't match the selected maintype
    Array.from(modelSelect.options).forEach(option => {
      const modelMainType = option.getAttribute("data-main-type");

      if (selectedMainType === "" || modelMainType === selectedMainType) {
        option.style.display = "block";  // Show option if it matches
      } else {
        option.style.display = "none";   // Hide option if it doesn't match
      }
    });

    // Optionally, clear the model selection if no matching models
    if (!Array.from(modelSelect.options).some(option => option.style.display === "block")) {
      modelSelect.value = "";
    }
  });

  document.getElementById("images-btn").addEventListener("click", function (event) {
    // Retrieve `sessionStorage` data
    const productId = sessionStorage.getItem('product-id');

    if (productId) {
      // Construct the URL with query parameters
      const url = `/images?product_id=${encodeURIComponent(productId)}`;

      // Open a new window with the constructed URL
      openWindow(url);
    } else {
      alert("يرجى اختيار عنصر");
      console.error('Missing sessionStorage values');
    }

  });
  document.getElementById("more-details-btn").addEventListener("click", function (event) {
    // Retrieve `sessionStorage` data
    const productId = sessionStorage.getItem('product-id');

    if (productId) {
      // Construct the URL with query parameters
      const url = `/more-details?product_id=${encodeURIComponent(productId)}`;

      // Open a new window with the constructed URL
      openWindow(url);
    } else {
      alert("يرجى اختيار عنصر");
      console.error('Missing sessionStorage values');
    }

  });
  // Helper function to get CSRF token
  function getCSRFToken() {
    const csrfTokenElement = document.querySelector('[name="csrfmiddlewaretoken"]');
    if (csrfTokenElement) {
      return csrfTokenElement.value;
    }
    // Try to get the CSRF token from the cookie if it's not in the form
    const csrfToken = document.cookie.match(/csrftoken=([^;]+)/);
    return csrfToken ? csrfToken[1] : '';
  }

  // Combined filter function
  function applyFilters() {
    console.log("applyFilters called");

    // Get selected item-main, skip if index is 0 (reset value)
    const itemMainSelect = document.getElementById("item-main");
    const selectedItemMainText = itemMainSelect.selectedIndex !== 0 ? itemMainSelect.options[itemMainSelect.selectedIndex].text : "";

    // Get selected item-sub-main, skip if index is 0 (reset value)
    const itemSubMainSelect = document.getElementById("item-sub-main");
    const selectedItemSubMainText = itemSubMainSelect.selectedIndex !== 0 ? itemSubMainSelect.options[itemSubMainSelect.selectedIndex].text : "";

    // Get selected company, skip if index is 0 (reset value)
    const companySelect = document.getElementById("company");
    const selectedCompanyText = companySelect.selectedIndex !== 0 ? companySelect.options[companySelect.selectedIndex].text : "";

    // Capture other field values
    const filterValues = {
      itemno: document.getElementById("original-no").value.trim().toLowerCase(),
      itemmain: selectedItemMainText,
      itemsubmain: selectedItemSubMainText,
      companyproduct: selectedCompanyText,
      itemname: document.getElementById("pname-arabic").value.trim().toLowerCase(),
      eitemname: document.getElementById("pname-english").value.trim().toLowerCase(),
      companyno: document.getElementById("company-no").value.trim().toLowerCase(),
      pno: document.getElementById("pno").value.trim().toLowerCase()
    };

    console.log("Filter values:", filterValues);

    // Function to get CSRF token from the DOM (if you're using Django's CSRF middleware)
    function getCSRFToken() {
      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
      return csrfToken;
    }

    // Define the datasource with filters applied
    const datasource = {
      getRows: function (params) {
        const startRow = params.startRow;
        const endRow = params.endRow;
        const filters = filterValues;

        // Create the URL with filter parameters
        const url = `/api/filter-items/?startRow=${startRow}&endRow=${endRow}`;

        // Fetch the data with filters
        fetch(url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),  // Include CSRF token here
          },
          body: JSON.stringify(filters),
        })
          .then(response => {
            if (!response.ok) {
              throw new Error("Network response was not ok");
            }
            return response.json();
          })
          .then(data => {
            // Pass the filtered data to AG Grid
            params.successCallback(data.rows, data.totalCount); // Pass rows and total count
          })
          .catch(error => {
            console.error("Error fetching filtered data:", error);
            params.failCallback(); // Call failCallback if fetch fails
          });
      }
    };

    // Set the new datasource to AG Grid
    agTable.api.setDatasource(datasource);
  }

  // Add event listeners to all filter inputs
  const filterInputs = [
    "original-no", "item-main", "item-sub-main", "pname-arabic", "pname-english", "company", "company-no", "pno"
  ];

  filterInputs.forEach((inputId) => {
    document.getElementById(inputId).addEventListener("input", applyFilters);
  });
  /*
    // Handle left-click on row to populate input fields
    agTable.api.addEventListener("rowClick", function (e, row) {
      if (e.button === 2) return; // 2 is right-click
      const rowData = row.getData();
      console.log(rowData);
      const fileid = rowData.fileid;// Assuming fileid is stored in the row's data-fileid attribute
      sessionStorage.setItem('product-id', fileid);
      sessionStorage.setItem('company-no', rowData.replaceno);
      sessionStorage.setItem('company-name', rowData.companyproduct);
  
      fetchItemData(fileid);
    });*/


  // Attach a click event to the "حذف" button
  document.getElementById("deleteButton").addEventListener("click", function () {
    // Check if a row is selected
    const selectedRow = agTable.api.getSelectedRows()[0]; // Get the first selected row
    if (selectedRow) {
      // Ask for confirmation before deletion
      if (confirm("هل أنت متأكد أنك تريد حذف هذا الصنف؟")) {
        // Get the file ID or primary key from the selected row data
        const fileId = selectedRow.fileid; // Replace 'fileid' with your actual field name

        // Call the function to delete the record from the server
        deleteRowFromServer(fileId)
          .then((success) => {
            if (success) {
              // If deletion was successful, remove the row from AG Grid
              agTable.api.applyTransaction({ remove: [selectedRow] });

              // Optionally clear form inputs if any
              clearForm();

              alert("تم حذف الصنف بنجاح.");
            } else {
              alert("حدث خطأ أثناء الحذف.");
            }
          })
          .catch((error) => {
            console.error("Error deleting record:", error);
            alert("حدث خطأ في الاتصال بالخادم.");
          });
      }
    } else {
      alert("من فضلك اختر سطرًا للحذف.");
    }
  });


  // Function to delete row from the server and return success status
  function deleteRowFromServer(fileid) {
    return new Promise((resolve, reject) => {
      // Get the CSRF token from the cookie or the template
      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

      // Use fetch to communicate with your backend and delete the record
      fetch('/delete-record/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,  // Add CSRF token here
        },
        body: JSON.stringify({ fileid: fileid }), // Send the fileid or any unique identifier for the record
      })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            resolve(true); // Return success
          } else {
            console.error("Deletion failed:", data.message || "Unknown error");
            resolve(false); // Return failure
          }
        })
        .catch(error => {
          console.error("Error during deletion request:", error);
          reject(error); // Reject on error
        });
    });
  }


  /*
    // Attach a rowClick event to select the row for deletion
    agTable.api.addEventListener("rowClick", function (e, row) {
      window.currentRow = row; // Save the selected row for later use
    });*/

  // Function to fetch item data and populate input fields
  function fetchItemData(fileid) {
    // Make an AJAX request to the Django backend
    fetch(`/get_item_data/${fileid}/`)
      .then(response => response.json())
      .then(data => {
        if (data.error) {
          alert("Item not found");
        } else {
          // Populate the input fields with the data from the response
          populateInputFields(data);
        }
      })
      .catch(error => {
        console.error("Error fetching data:", error);
      });
  }


  // Populate input fields with row data
  function populateInputFields(data) {
    // For 'countries' dropdown (set selected item based on 'data.itemsize')
    const countrySelect = document.getElementById("countries");
    const countryOptions = countrySelect.options;
    let countrySelected = false;  // Flag to track if a match is found
    for (let i = 0; i < countryOptions.length; i++) {
      if (countryOptions[i].text === data.itemsize) {  // Compare text (country name)
        countrySelect.selectedIndex = i;  // Set the selected option
        countrySelected = true;  // Mark as selected
        break;
      }
    }
    if (!countrySelected) {  // Reset if no match found
      countrySelect.selectedIndex = 0;  // Set the selected option to the first one
    }

    // For 'item-main' dropdown (set selected item based on 'data.itemmain')
    const itemMainSelect = document.getElementById("item-main");
    const itemMainOptions = itemMainSelect.options;
    let itemMainSelected = false;  // Flag to track if a match is found
    for (let i = 0; i < itemMainOptions.length; i++) {
      if (itemMainOptions[i].text === data.itemmain) {  // Compare text (item main)
        itemMainSelect.selectedIndex = i;  // Set the selected option
        itemMainSelected = true;  // Mark as selected
        break;
      }
    }
    if (!itemMainSelected) {  // Reset if no match found
      itemMainSelect.selectedIndex = 0;  // Set the selected option to the first one
    }

    // For 'item-sub-main' dropdown (set selected item based on 'data.itemsubmain')
    const itemSubMainSelect = document.getElementById("item-sub-main");
    const itemSubMainOptions = itemSubMainSelect.options;
    let itemSubMainSelected = false;  // Flag to track if a match is found
    for (let i = 0; i < itemSubMainOptions.length; i++) {
      if (itemSubMainOptions[i].text === data.itemsubmain) {  // Compare text (item sub main)
        itemSubMainSelect.selectedIndex = i;  // Set the selected option
        itemSubMainSelected = true;  // Mark as selected
        break;
      }
    }
    if (!itemSubMainSelected) {  // Reset if no match found
      itemSubMainSelect.selectedIndex = 0;  // Set the selected option to the first one
    }

    // For 'company' dropdown (set selected item based on 'data.companyproduct')
    const companySelect = document.getElementById("company");
    const companyOptions = companySelect.options;
    let companySelected = false;  // Flag to track if a match is found
    for (let i = 0; i < companyOptions.length; i++) {
      if (companyOptions[i].text === data.companyproduct) {  // Compare text (company name)
        companySelect.selectedIndex = i;  // Set the selected option
        companySelected = true;  // Mark as selected
        break;
      }
    }
    if (!companySelected) {  // Reset if no match found
      companySelect.selectedIndex = 0;  // Set the selected option to the first one
    }

    // For 'model' dropdown (set selected item based on 'data.model')
    const modelSelect = document.getElementById("model");
    const modelOptions = modelSelect.options;
    let modelSelected = false;  // Flag to track if a match is found
    for (let i = 0; i < modelOptions.length; i++) {
      if (modelOptions[i].text === data.itemthird) {  // Compare text (model name)
        modelSelect.selectedIndex = i;  // Set the selected option
        modelSelected = true;  // Mark as selected
        break;
      }
    }
    if (!modelSelected) {  // Reset if no match found
      modelSelect.selectedIndex = 0;  // Set the selected option to the first one
    }

    document.getElementById("original-no").value = data.itemno || "";
    document.getElementById("pname-arabic").value = data.itemname || "";
    document.getElementById("pname-english").value = data.eitemname || "";
    document.getElementById("company-no").value = data.replaceno || "";
    document.getElementById("pno").value = data.pno || "";
    document.getElementById("barcode-no").value = data.barcodeno || "";
    document.getElementById("description").value = data.memo || "";
    document.getElementById("pieces-per-box").value = data.itemperbox || "";
    document.getElementById("storage-balance").value = data.itemvalue || "";
    document.getElementById("backup-balance").value = data.itemtemp || "";
    document.getElementById("temp-balance").value = data.itemvalueb || "";
    document.getElementById("reserved-balance").value = data.reservedvalue || "";
    document.getElementById("location").value = data.itemplace || "";
    document.getElementById("origin-price").value = data.orgprice || "";
    document.getElementById("buy-price").value = data.orderprice || "";
    document.getElementById("expenses-price").value = data.costprice || "";
    document.getElementById("sell-price").value = data.buyprice || "";
    document.getElementById("less-price").value = data.lessprice || "";
  }

  document.getElementById("reset-button").addEventListener("click", clearForm);
  document.getElementById("new-record-button").addEventListener("click", createNewRecord);

  function fetchAllData(params) {
    const url = document.getElementById('users-table').getAttribute('data-url');  // Get the URL from the table's data-url attribute

    // Use the URL in your fetch request
    fetch(url + `?startRow=${params.startRow}&endRow=${params.endRow}`)
      .then((response) => response.json())  // Parse the response as JSON
      .then((data) => {
        console.log("Fetched Data:", data);  // Log the fetched data (optional)

        // Provide the rows and lastRow (number of total rows)
        params.successCallback(data.rows, data.totalCount);
      })
      .catch((error) => {
        console.error("Error fetching data:", error);  // Handle errors
        params.failCallback();  // Optionally, call failCallback on error
      });
  }


  function clearForm() {
    window.requestAnimationFrame(function () {
      const formElements = document.querySelectorAll('form input, form select, form textarea');
      formElements.forEach(function (element) {
        if (element.tagName.toLowerCase() === 'input' || element.tagName.toLowerCase() === 'textarea') {
          element.value = '';  // Reset input and textarea values
        } else if (element.tagName.toLowerCase() === 'select') {
          element.selectedIndex = 0;  // Reset select dropdowns
        }
      });



      // Clear any filters applied in AG Grid
      if (agTable) {
        agTable.api.setFilterModel(null);  // Clear any applied filters

        // Optionally, clear the data or fetch fresh data (based on your need)
        fetchAllData();  // Fetch the full dataset or reset to initial state
      }
    });
  }



});



// Initialize all tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl);
});

let childWindows = [];

function openWindow(url) {
  // Get the parent window's dimensions and position
  const parentWidth = window.innerWidth;
  const parentHeight = window.innerHeight;
  const parentLeft = window.screenX;
  const parentTop = window.screenY;

  // Calculate the center position for the child window
  const width = 600;
  const height = 700;
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
      childWindows = childWindows.filter(win => win !== childWindow);
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
    childWindows.forEach(win => {
      if (!win.closed) {
        win.close();
      }
    });
  };
}







// Allow editing of table cells
const editableCells = document.querySelectorAll(".editable");


editableCells.forEach((cell) => {
  cell.addEventListener("dblclick", () => {
    cell.setAttribute("contenteditable", "true");
    cell.focus();
  });

  cell.addEventListener("blur", () => {
    const userId = cell.getAttribute("data-id");
    const column = cell.cellIndex; // Get the index of the cell
    const newValue = cell.innerText;

    // Send the updated value to the server if contenteditable is set to false
    if (cell.getAttribute("contenteditable") === "false") {
      return;
    }

    // Send the updated value to the server
    fetch("/update-user", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        id: userId,
        column: column, // Specify which column is being updated
        value: newValue,
      }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        console.log("Success:", data);
      })
      .catch((error) => {
        console.error("Error:", error);
      });

    // Set contenteditable to false after the fetch call
    cell.setAttribute("contenteditable", "false");
  });

  cell.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault(); // Prevent adding new lines
      cell.blur(); // Trigger blur to save changes
    }
  });
});

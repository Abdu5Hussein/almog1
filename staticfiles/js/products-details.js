console.log("Script Loaded");

document.addEventListener("DOMContentLoaded", function () {
  const jwtToken_access = localStorage.getItem("session_data@access_token").replace(/"/g, '');
  console.log("jwt access token: " + jwtToken_access);

  function EmptyRequiredFields() {
    const fields = [
      //document.getElementById('pno'),
      document.getElementById('pname-arabic'),
      document.getElementById('company'),
      document.getElementById('company-no'),
      document.getElementById('item-main'),
      //document.getElementById('storage-balance'),
      document.getElementById('origin-price'),
    ]
    for (let i = 0; i < fields.length; i++) {
      // Check if the field is empty
      if (!fields[i].value.trim()) {
        return true; // Return true if any field is empty
      }
    }
    return false; // Return false if all fields are not empty
  }

  const csrfToken = $("meta[name='csrf-token']").attr("content");
  if (csrfToken) {
    console.log("token exist");
  }

  let currentPage = 1; // Tracks the current page
  let lastPage = false; // Indicates if the last page is reached
  let isLoading = false; // Prevents multiple fetch calls
  const pageSize = 100; // Number of rows per page
  const tableContainer = document.getElementById("users-table");// Table scroll container
  // Function to fetch and append the next page of data
  const fetchNextPage = () => {
    if (!lastPage) {
      currentPage++;
      console.log(`Fetching page ${currentPage}...`);
      console.log("fetching active url : ", active_url);

      if (active_url == "server_filtered_data") {
        //console.log("apply filters current page: ",currentPage);
        applyFilters(currentPage, pageSize);
      } else {
        fetchDataFromServer({ page: currentPage, size: pageSize });
      }
      //hideLoader();
    }
  };
  //////////
  const fullTable = document.getElementById("fullTable");

  // Add an event listener for the 'change' event
  fullTable.addEventListener("change", () => {
    fetchDataFromServer();
  });


  /////////////
  // Scroll event listener
  const handleScroll = () => {
    //console.log("scroll area");
    const scrollPosition = tableContainer.scrollTop + tableContainer.clientHeight;
    const scrollThreshold = tableContainer.scrollHeight - 2000; // Adjust threshold as needed
    console.log("isLoading: ", isLoading);
    console.log("lastPage: ", lastPage);

    if (scrollPosition >= scrollThreshold && !lastPage && !isLoading) {
      console.log("scrollPosition: ", scrollPosition);
      console.log("scrollThreshold: ", scrollThreshold);
      console.log("scrollHeight: ", tableContainer.scrollHeight);
      //console.log("lastPage: ",lastPage);
      //console.log("isLoading: ",isLoading);
      isLoading = true;
      showLoader();
      fetchNextPage();
    }
  };
  function fetchDataFromServer({ page = 1, size = 100 } = {}) {
    const fullTable = document.getElementById("fullTable");
    const full = fullTable.checked;
    if (full == true) {

      console.log("Fetching full table");
      console.time("fetchData"); // Start timer

      fetch(`api/get-data/?fullTable=${full}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ////'Authorization': `Bearer ${jwtToken_access}`  // 👈 Include JWT token
        }
      }).then((response) => response.json())
        .then((data) => {
          console.log("Fetched Data:", data);

          console.time("tableTime");
          table.setData(data.data);
          console.timeEnd("tableTime");

          // Update lastPage flag
          lastPage = true;
          console.time("PaginationTime");
          updatePagination(1, 1);
          console.timeEnd("PaginationTime");

          return data; // Return data for further processing
        })
        .catch((error) => console.error("Error fetching data:", error)).finally(() => {
          console.timeEnd("fetchData"); // End the timer regardless of success or failure
          isLoading = false; // Reset loading flag after fetch completes
          hideLoader();
        });


      return;
    }
    // Use the URL in your fetch request
    console.time("fetchData"); // Start timer

    fetch(`api/get-data/?page=${page}&size=${size}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ////'Authorization': `Bearer ${jwtToken_access}`  // 👈 Include JWT token
      }
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Fetched Data:", data);
        active_url = "server_Data_No_Filter";
        console.log("active_url for pagination:", active_url);
        //console.log("page:", page);

        console.time("tableTime");
        //console.log("sort status: ", table.getDataCount());
        if (page === 1) {
          // For the first page, replace the existing data
          table.setData(data.data);
          console.log("data set to the table");
          //console.log("getDataCount: ", table.getDataCount());
          currentPage = 1;
        } else {
          let scrollPosition = tableContainer.scrollTop; // Save scroll position
          //let currentData = table.getData();  // Get current table data
          //let combinedData = currentData.concat(data.data);  // Combine existing data with new data
          table.addData(data.data);
          tableContainer.scrollTop = scrollPosition;
          console.log("data added to the table");
          //console.log("getDataCount: ", table.getDataCount());
        }
        console.timeEnd("tableTime");

        // Update lastPage flag
        lastPage = data.page_no == data.last_page ? true : false;
        console.time("PaginationTime");
        updatePagination(data.last_page, data.page_no);
        console.timeEnd("PaginationTime");


        return data; // Return data for further processing
      })
      .catch((error) => console.error("Error fetching data:", error)).finally(() => {
        console.timeEnd("fetchData"); // End the timer regardless of success or failure
        isLoading = false; // Reset loading flag after fetch completes
        hideLoader();
      });
  }
  // Attach the scroll event listener
  tableContainer.addEventListener("scroll", handleScroll);


  fetchDataFromServer({ page: 1, size: 100 });



  const url = document.getElementById('users-table').getAttribute('data-url');

  // Use the URL in your fetch request
  /*fetch(url)
    .then((response) => response.json())
    .then((data) => {
      console.log("Fetched Data:", data);
      table.setData(data.data);
    })
    .catch((error) => console.error("Error fetching data:", error));*/

  ////////////////////
  // Initialize Tabulator
  const table = new Tabulator("#users-table", {
    height: "auto", // Adjust height or set a fixed height
    layout: "fitColumns",
    selectable: true,
    rowHeight: 20,
    movableColumns: true,
    columnHeaderVertAlign: "bottom",
    columnMenu: true, // Enable column menu
    data: [], // Placeholder, will be loaded dynamically
    columns: [
      // Column definitions
      { title: "الرقم الخاص", field: "pno", headerMenu: false, width: 100, visible: true },
      { title: "الشركة المصنعة", field: "companyproduct", headerMenu: false, width: 96, visible: true },
      { title: "رقم الشركة", field: "replaceno", headerMenu: false, width: 150, visible: true },
      { title: "الرقم الاصلي", field: "itemno", headerMenu: false, width: 90, visible: true },
      { title: "اسم الصنف ع", field: "itemname", headerMenu: false, width: 280, visible: true },
      { title: "الرصيد", field: "itemvalue", headerMenu: false, width: 81, visible: true },
      { title: "سعر البيع", field: "buyprice", headerMenu: false, width: 75, visible: true },
      { title: "الموقع", field: "itemplace", headerMenu: false, width: 75, visible: true },
      { title: "رقم الملف", field: "fileid", visible: false },
      { title: "البيان الرئيسي", field: "itemmain", visible: false },
      { title: "البيان الفرعي", field: "itemsubmain", visible: false },
      { title: "الموديل", field: "itemthird", visible: false },
      { title: "بلد الصنع", field: "itemsize", visible: false },
      { title: "Date Product", field: "dateproduct", visible: false },
      { title: "Level Product", field: "levelproduct", visible: false },
      { title: "الرصيد الاحتياطي", field: "itemtemp", visible: false },
      { title: "تاريخ اخر طلب", field: "orderlastdate", visible: false },
      { title: "مصدر الطلب", field: "ordersource", visible: false },
      { title: "رقم فاتورة الطلب", field: "orderbillno", visible: false },
      { title: "تاريخ اخر شراء", field: "buylastdate", visible: false },
      { title: "مصدر الشراء", field: "buysource", visible: false },
      { title: "رقم فاتورة الشراء", field: "buybillno", visible: false },
      { title: "سعر التوريد", field: "orgprice", visible: false },
      { title: "سعر الشراء", field: "orderprice", visible: false },
      { title: "سعر التكلفة", field: "costprice", visible: false },
      { title: "المواصفات", field: "memo", visible: false },
      { title: "Order Stop", field: "orderstop", visible: false },
      { title: "Buy Stop", field: "buystop", visible: false },
      { title: "Item Trans", field: "itemtrans", visible: false },
      { title: "الرصيد المؤقت", field: "itemvalueb", visible: false },
      { title: "Item Type", field: "itemtype", visible: false },
      { title: "رقم الباركود", field: "barcodeno", visible: false },
      { title: "اسم الصنف بالانجليزي", field: "eitemname", visible: false },
      { title: "عملة الشراء", field: "currtype", visible: false },
      { title: "اقل سعر", field: "lessprice", visible: false },
      { title: "قيمة العملة", field: "currvalue", visible: false },
      { title: "الرصيد المحجوز", field: "resvalue", visible: false },
      { title: "عدد القطع للصندوق", field: "itemperbox", visible: false },
      { title: "حالة الصنف", field: "cstate", visible: false },
    ],
    placeholder: "No Data Available",
    rowFormatter: function (row) {
      // Set the height directly on each row
      row.getElement().style.height = "20px";

      var rowData = row.getData();  // Get the row data
      var itemvalue = parseInt(rowData.itemvalue); // Access specific column data
      var itemvalueb = parseInt(rowData.itemvalueb);
      var buyprice = parseFloat(rowData.buyprice);  // Ensure buyprice is a number
      var costprice = parseFloat(rowData.costprice);
      var itemtemp = parseInt(rowData.itemtemp);
      var orgprice = parseFloat(rowData.orgprice);
      var orderprice = parseFloat(rowData.orderprice);

      // Ensure costprice is a number
      if (itemvalue <= itemtemp) {
        row.getElement().style.backgroundColor = "#ffffe0"; // Apply yellow row class
      }
      if (itemvalue == 0 && itemvalueb == 0) {
        row.getElement().style.backgroundColor = "#ffc0c0"; // Apply red row class
      }
      if (costprice > buyprice) {
        row.getElement().style.backgroundColor = "#ffdab9"; // Apply orange row class
      }
      if (itemvalueb > 0) {
        row.getElement().style.backgroundColor = "#d8f3dc"; // Apply green row class
      }
      if (costprice == 0 || orderprice == 0 || orgprice == 0) {
        row.getElement().style.backgroundColor = "red"; // Apply red row class
      }


      // You can add more conditions as needed
    }, // Message when no data is present or after filtering
    rowClick: function (e, row) {
      console.log("Row clicked", row);
      row.select(); // Select the clicked row
    },
    tableBuilt: function () {
      console.log('table built');
      // After the table is built, set up column visibility handlers
      setupColumnVisibilityHandlers(table);

      // Set checkboxes based on column visibility
      table.getColumns().forEach((column) => {
        const columnField = column.getField();
        const checkbox = document.querySelector(`#column-menu input[value="${columnField}"]`);

        if (checkbox) {
          checkbox.checked = column.isVisible(); // Update checkbox based on column visibility
        }
      });
    },

  });
  table.options.tableBuilt();

  ////////////////////

  // Show/Hide dropdown menu on button click
  document.getElementById("toggle-column-menu").addEventListener("click", function () {
    const dropdown = document.getElementById("column-menu");
    dropdown.style.display = dropdown.style.display === "none" || dropdown.style.display === "" ? "block" : "none";
  });

  // Column visibility handlers (attach to checkboxes after table initialization)
  function setupColumnVisibilityHandlers(table) {
    document.querySelectorAll('#column-menu input[type="checkbox"]').forEach((checkbox) => {
      checkbox.addEventListener("change", function () {
        const columnField = this.value;
        if (this.checked) {
          table.showColumn(columnField); // Show the column
        } else {
          table.hideColumn(columnField); // Hide the column
        }
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

  table.on("rowSelectionChanged", function () {
    const selectedRows = table.getSelectedRows();
    console.log("Selected Rows:", selectedRows); // Log when selection changes
  });


  // Prevent default context menu within #users-table div
  $("#users-table").on("contextmenu", function (e) {
    e.preventDefault(); // Prevent default right-click menu on table
  });

  // Handle right-click on row
  table.on("rowContext", function (e, row) {
    e.preventDefault();
    window.currentRow = row; // Save row for later use in performAction
    const contextMenu = document.getElementById("contextMenu");
    contextMenu.style.left = `${e.pageX}px`;
    contextMenu.style.top = `${e.pageY}px`;
    contextMenu.style.display = "block";
  });

  // Hide custom context menu when clicking outside
  document.addEventListener("click", function (e) {
    const contextMenu = document.getElementById("contextMenu");
    if (!e.target.closest("#contextMenu") && !e.target.closest("#users-table")) {
      contextMenu.style.display = "none"; // Hide context menu
    }
  });

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
  };



  // Function to get CSRF token
  function getCSRFToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]").value;
  }
  function createNewRecord() {
    const getValueById = (id) => {
      const element = document.getElementById(id);
      return element ? element.value.trim() : "";
    };

    const getSelectedTextById = (id) => {
      const element = document.getElementById(id);
      return element && element.selectedIndex !== 0
        ? element.options[element.selectedIndex].text
        : "";
    };

    const getChoicesTextById = (id) => {
      const element = document.getElementById(id);
      return element ? element.getValue(true).join("; ") : "";
    };

    if (EmptyRequiredFields()) {
      alert('! الرجاء ملئ الحقول المطلوبة !')
      return
    }

    // Data object with correct CSRF token retrieval
    const data = {
      csrfmiddlewaretoken: getCSRFToken(),
      originalno: getValueById("original-no") || "",
      itemmain: getSelectedTextById("item-main") || "",
      itemsub: getSelectedTextById("item-sub-main") || "",
      pnamearabic: getValueById("pname-arabic") || "",
      pnameenglish: getValueById("pname-english") || "",
      company: getSelectedTextById("company"),
      companyno: getValueById("company-no") || "",
      pno: getValueById("pno") || "",
      barcode: getValueById("barcode-no") || "",
      description: getValueById("description") || "",
      country: getSelectedTextById("country") || "",
      pieces4box: getValueById("pieces-per-box") || 0,
      model: getSelectedTextById("model") || "",
      storage: getValueById("storage-balance") || 0,
      backup: getValueById("backup-balance") || 0,
      temp: getValueById("temp-balance") || 0,
      reserved: getValueById("reserved-balance") || 0,
      location: getValueById("location") || "",
      originprice: getValueById("origin-price") || 0,
      buyprice: getValueById("buy-price") || 0,
      expensesprice: getValueById("expenses-price") || 0,
      sellprice: getValueById("sell-price") || 0,
      lessprice: getValueById("less-price") || 0,
      shortname: getValueById("short-name") || null,
      engine: getSelectedTextById("engine") || null,
    };

    console.log(data);

    fetch("/create_main_item/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(), // Add the CSRF token here
        //'Authorization': `Bearer ${jwtToken_access}`,
      },
      body: JSON.stringify(data),
    })
      .then((response) => {
        if (response.ok) {
          alert("Record created successfully!");
          fetchDataFromServer({ page: 1, size: pageSize });

        } else {
          alert("Error creating record.");
          console.log(getCSRFToken()); // Check the value of the CSRF token
        }
      })
      .catch((error) => console.error("Error:", error));
  }

  const getValueById = (id) => {
    const element = document.getElementById(id);
    return element ? element.value.trim() : "";
  };

  const getSelectedTextById = (id) => {
    const element = document.getElementById(id);
    return element && element.selectedIndex !== 0
      ? element.options[element.selectedIndex].text
      : "";
  };

  const getChoicesTextById = (id) => {
    const element = document.getElementById(id);
    return element ? element.getValue(true).join("; ") : "";
  };

  ////edit function
  document.getElementById("editButton").addEventListener("click", function (event) {
    event.preventDefault(); // Prevent form submission

    // if (EmptyRequiredFields()) {
    //   alert('! الرجاء ملئ الحقول المطلوبة !')
    //   return
    // }

    if (window.currentRow) {
      // Get the data from the form fields using helper functions
      const data = {
        csrfmiddlewaretoken: getCSRFToken(),
        fileid: window.currentRow.getData().fileid,
        originalno: getValueById("original-no"),
        itemmain: getSelectedTextById("item-main"),
        itemsub: getSelectedTextById("item-sub-main"),
        pnamearabic: getValueById("pname-arabic"),
        pnameenglish: getValueById("pname-english"),
        company: getSelectedTextById("company"),
        companyno: getValueById("company-no"),
        pno: getValueById("pno"),
        barcode: getValueById("barcode-no"),
        description: getValueById("description"),
        country: getSelectedTextById("countries"),
        pieces4box: getValueById("pieces-per-box") || 0,
        model: getSelectedTextById("model"),
        storage: getValueById("storage-balance") || 0,
        backup: getValueById("backup-balance") || 0,
        temp: getValueById("temp-balance") || 0,
        reserved: getValueById("reserved-balance") || 0,
        location: getValueById("location") || "",
        originprice: getValueById("origin-price") || 0,
        buyprice: getValueById("buy-price") || 0,
        expensesprice: getValueById("expenses-price") || 0,
        sellprice: getValueById("sell-price") || 0,
        lessprice: getValueById("less-price") || 0,
        shortname: getValueById("short-name") || null,
        engine: getSelectedTextById("engine") || null,
      };

      // Send the data to the server via a PATCH request
      fetch("/edit_main_item/", {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
          //'Authorization': `Bearer ${jwtToken_access}`,
        },
        body: JSON.stringify(data),
      })
        .then((response) => {
          if (response.ok) {
            alert("Record updated successfully!");
            fetchDataFromServer({ page: 1, size: pageSize });

            // Optionally update the row directly in Tabulator
            const updatedRowData = { ...window.currentRow.getData(), ...data };
            window.currentRow.update(updatedRowData);
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
    const fileid = sessionStorage.getItem('product-id');
    const data = {
      companyno: companyNo,
      fileid: fileid,
      company: companyName,
    }
    console.log(data);
    if (companyName && companyNo) {

      fetch("/oem/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
          //'Authorization': `Bearer ${jwtToken_access}`,
        },
        body: JSON.stringify(data),
      })
        .then((response) => {
          // Check if the response is a redirect (3xx status code)
          if (response.redirected) {
            // Open the new URL in a new window/tab
            openWindow(response.url);
            return;
          }

          // If the response is JSON, handle it accordingly
          return response.json();
        })
        .then((data) => {
          if (data) {
            console.log("Response from server:", data);
            if (data.success) {
              console.log("Invoice sent successfully!");
            } else {
              console.log("Error updating invoice:", data.message);
            }
          }
        })
        .catch((error) => {
          console.error("Error during fetch:", error);
          alert("An error occurred: " + error.message);
        });

    } else {
      alert("يرجى اختيار عنصر");
      console.error('Missing sessionStorage values');
    }

  });


  /////////////
  // document.getElementById("item-main").addEventListener("change", function () {
  //   const selectedMainType = this.value.trim(); // Get selected value
  //   const subMainSelect = document.getElementById("item-sub-main");

  //   // Show only options where data-main-type matches selected item-main
  //   Array.from(subMainSelect.options).forEach(option => {
  //     if (option.value === "") {
  //       option.hidden = false; // Keep default option visible
  //       option.selected = true; // Reset selection
  //     } else {
  //       option.hidden = option.getAttribute("data-main-type") !== selectedMainType;
  //     }
  //   });

  //   // Reset model selection when item-main changes
  //   document.getElementById("model").innerHTML = '<option value="" selected>اختر موديل</option>';
  // });


  const itemMainSelect = document.getElementById("item-main");
  const itemSubMainSelect = document.getElementById("item-sub-main");
  const modelSelect = document.getElementById("model");

  // Function to filter options based on a data attribute
  const filterOptions = (selectElement, attribute, selectedValue) => {
    Array.from(selectElement.options).forEach(option => {
      if (option.value === "") {
        option.hidden = false; // Keep default option visible
        option.selected = true; // Reset selection
      } else {
        option.hidden = option.getAttribute(attribute) !== selectedValue;
      }
    });
  };

  // Event listener for item-main selection
  itemMainSelect.addEventListener("change", function () {
    const selectedMainType = this.value.trim();
    filterOptions(itemSubMainSelect, "data-main-type", selectedMainType);

    // Reset model options when item-main changes
    //modelSelect.innerHTML = '<option value="" selected>اختر موديل</option>';
  });

  // Event listener for item-sub-main selection
  itemSubMainSelect.addEventListener("change", function () {
    const selectedSubType = this.value.trim();
    filterOptions(modelSelect, "data-sub-type", selectedSubType);
  });

  //////////////


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
  function applyFilters(pageno = 1, pagesize = pageSize) {
    console.time("applyFiltersTime");

    // Cache DOM elements for improved performance
    const filterElements = {
      itemno: document.getElementById("original-no"),
      itemmain: document.getElementById("item-main"),
      itemsubmain: document.getElementById("item-sub-main"),
      companyproduct: document.getElementById("company"),
      itemname: document.getElementById("pname-arabic"),
      companyno: document.getElementById("company-no"),
      eitemname: document.getElementById("pname-english"),
      pno: document.getElementById("pno"),
    };

    console.time("inputsTime");

    // Helper function to get element values
    const getValue = (element) => (element ? element.value.trim().toLowerCase() : "");
    const getSelectedText = (element) =>
      element && element.selectedIndex !== 0
        ? element.options[element.selectedIndex].text
        : "";
    const getChoicesText = (element) =>
      element ? element.getValue(true).join("; ") : "";
    // Capture filter values

    const filterValues = {
      itemno: getValue(filterElements.itemno),
      itemmain: getSelectedText(filterElements.itemmain),
      itemsubmain: getSelectedText(filterElements.itemsubmain),
      companyproduct: getSelectedText(filterElements.companyproduct),
      itemname: getValue(filterElements.itemname),
      eitemname: getValue(filterElements.eitemname),
      companyno: getValue(filterElements.companyno),
      pno: getValue(filterElements.pno),
      page: parseInt(pageno, 10) || 1,
      size: pagesize || 100,
      fullTable: document.getElementById("fullTable").checked,
    };
    console.log("filter values: ", filterValues);


    console.timeEnd("inputsTime");

    // Check if all filter values are empty (except page and size)
    const isFiltersEmpty = Object.entries(filterValues).every(
      ([key, value]) => ["page", "size"].includes(key) || !value
    );

    if (isFiltersEmpty) {
      fetchDataFromServer({ page: 1, size: pageSize });
      console.timeEnd("applyFiltersTime");
      return;
    }

    // Prepare and send the request
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";

    console.time("FilterTime");

    fetch("/api/filter-items", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
        //'Authorization': `Bearer ${jwtToken_access}`,
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

        // Update Tabulator table
        if (pageno === 1) {
          table.replaceData(data.data);
          currentPage = 1;
        } else {
          const scrollPosition = tableContainer.scrollTop;
          table.addData(data.data);
          tableContainer.scrollTop = scrollPosition;
        }

        lastPage = data.page_no === data.last_page;

        console.timeEnd("tableTime");

        console.time("PaginationTime");
        updatePagination(data.last_page, data.page_no);
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
        hideLoader();
      });
  }

  // Debounce function definition
  function debounce(func, wait) {
    let timeout;
    return function (...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), wait);
    };
  }

  // Apply debounce to applyFilters with a 300ms delay
  const debouncedApplyFilters = debounce(() => applyFilters(1), 390);

  // Add event listeners to all filter inputs
  const filterInputs = [
    "original-no", "item-main", "item-sub-main", "pname-arabic", "pname-english", "company", "company-no", "pno"
  ];

  filterInputs.forEach((inputId) => {
    document
      .getElementById(inputId)
      .addEventListener("input", () => {
        debouncedApplyFilters();
      });
  });

  // Handle left-click on row to populate input fields
  table.on("rowClick", function (e, row) {
    if (e.button === 2) return; // 2 is right-click
    const rowData = row.getData();
    console.log(rowData);
    const fileid = rowData.fileid;// Assuming fileid is stored in the row's data-fileid attribute
    sessionStorage.setItem('product-id', fileid);
    sessionStorage.setItem('company-no', rowData.replaceno);
    sessionStorage.setItem('company-name', rowData.companyproduct);
    sessionStorage.setItem('pno', rowData.pno);

    fetchItemData(fileid);
  });


  // Attach a click event to the "حذف" button
  document.getElementById("deleteButton").addEventListener("click", function () {
    if (window.currentRow) {
      // Ask for confirmation before deletion
      if (confirm("هل أنت متأكد أنك تريد حذف هذا الصنف؟")) {
        // Get the row data to send to the server
        const rowData = window.currentRow.getData(); // Get the row data (make sure fileid exists)

        // Call the function to delete the record from the server
        deleteRowFromServer(rowData.fileid)
          .then(success => {
            if (success) {
              // If deletion was successful, delete the row from Tabulator
              window.currentRow.delete();

              // Hide the context menu if it's open
              const contextMenu = document.getElementById("contextMenu");
              contextMenu.style.display = "none";
              clearForm();

              alert("تم حذف الصنف بنجاح.");
            } else {
              alert("حدث خطأ أثناء الحذف.");
            }
          })
          .catch(error => {
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
          //'Authorization': `Bearer ${jwtToken_access}`,
        },
        body: JSON.stringify({ fileid: fileid }), // Send the fileid or any unique identifier for the record
      })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            resolve(true); // Return success
          } else {
            resolve(false); // Return failure
          }
        })
        .catch(error => {
          reject(error); // Reject on error
        });
    });
  }


  // Attach a rowClick event to select the row for deletion
  table.on("rowClick", function (e, row) {
    window.currentRow = row; // Save the selected row for later use
  });

  // Function to fetch item data and populate input fields
  function fetchItemData(fileid) {
    console.log("item with file id: ", fileid);
    // Make an AJAX request to the Django backend
    fetch(`/get_item_data/${fileid}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        //'Authorization': `Bearer ${jwtToken_access}`  // 👈 Include JWT token
      }
    })
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
    clearForm(false);

    setDropdownValue("countries", data.itemsize, "اختر دولة");
    setDropdownValue("item-main", data.itemmain, "اختر بيان رئيسي");
    setDropdownValue("item-sub-main", data.itemsubmain, "اختر بيان فرعي");
    setDropdownValue("company", data.companyproduct, "اختر شركة");
    setDropdownValue("model", data.itemthird, "اختر موديل");
    setDropdownValue("engine", data.engine_no, "اختر محرك");

    setPlaceholder("original-no", data.itemno);
    setPlaceholder("pname-arabic", data.itemname);
    setPlaceholder("pname-english", data.eitemname);
    setPlaceholder("company-no", data.replaceno);
    setPlaceholder("pno", data.pno);
    setPlaceholder("barcode-no", data.barcodeno);
    setPlaceholder("description", data.memo);
    setPlaceholder("pieces-per-box", data.itemperbox);
    setPlaceholder("storage-balance", data.itemvalue, "0");
    setPlaceholder("backup-balance", data.itemtemp, "0");
    setPlaceholder("temp-balance", data.itemvalueb, "0");
    setPlaceholder("reserved-balance", data.reservedvalue, "0");
    setPlaceholder("location", data.itemplace);
    setPlaceholder("origin-price", data.orgprice, "0");
    setPlaceholder("buy-price", data.orderprice, "0");
    setPlaceholder("expenses-price", data.costprice, "0");
    setPlaceholder("sell-price", data.buyprice, "0");
    setPlaceholder("less-price", data.lessprice, "0");
    setPlaceholder("short-name", data.short_name);
  }

  function setDropdownValue(elementId, value, defaultText) {
    const select = document.getElementById(elementId);
    const options = select.options;
    let found = false;

    for (let i = 0; i < options.length; i++) {
      if (options[i].text === value) {
        select.selectedIndex = i;
        found = true;
        break;
      }
    }

    if (!found) {
      options[0].text = value || defaultText;
      select.selectedIndex = 0;
    }
  }

  function setPlaceholder(elementId, value, defaultValue = "") {
    document.getElementById(elementId).placeholder = value || defaultValue;
  }


  document.getElementById("reset-button").addEventListener("click", clearForm);
  document.getElementById("new-record-button").addEventListener("click", createNewRecord);

  function fetchAllData() {
    const url = document.getElementById('users-table').getAttribute('data-url');  // Get the URL from the table's data-url attribute

    // Use the URL in your fetch request
    fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        //'Authorization': `Bearer ${jwtToken_access}`  // 👈 Include JWT token
      }
    })
      .then((response) => response.json())  // Parse the response as JSON
      .then((data) => {
        console.log("Fetched Data:", data);  // Log the fetched data (optional)
        table.setData(data);  // Update your table with the fetched data
      })
      .catch((error) => console.error("Error fetching data:", error));  // Handle errors
  }

  function clearForm(flag = true) {
    if (flag == false) {
      const formElements = document.querySelectorAll('form input, form select, form textarea');
      formElements.forEach(function (element) {
        if (element.tagName.toLowerCase() === 'input' || element.tagName.toLowerCase() === 'textarea') {
          element.value = '';
          element.placeholder = '';
        } else if (element.tagName.toLowerCase() === 'select') {
          element.selectedIndex = 0;  // Reset select dropdowns
          element.options[0].text = 'اختر قيمة';
        }
      });
      return
    }
    window.requestAnimationFrame(function () {
      const formElements = document.querySelectorAll('form input, form select, form textarea');
      formElements.forEach(function (element) {
        if (element.tagName.toLowerCase() === 'input' || element.tagName.toLowerCase() === 'textarea') {
          element.value = '';  // Reset input and textarea values
          element.placeholder = '';
        } else if (element.tagName.toLowerCase() === 'select') {
          element.selectedIndex = 0;  // Reset select dropdowns
          element.options[0].text = 'اختر قيمة';
        }
      });



      // Clear any filters applied in the table (Tabulator's clearFilter method)
      // Clear any applied filters in Tabulator
      if (table) {
        table.clearFilter(); // Clear all filters applied
        fetchDataFromServer({ page: 1, size: pageSize });
        //console.log("Filters cleared");
      }
    });
  }

  function updatePagination(lastPage, currentPage) {
    const pagination = document.querySelector(".pagination");
    const existingPageLinks = pagination.querySelectorAll(".page-item:not(:first-child):not(:last-child):not(#page-size)");
    //console.log("existingPageLinks: ",existingPageLinks);

    const startPage = Math.max(1, currentPage);
    const endPage = Math.min(lastPage, startPage + 2);
    //console.log("startPage: ",startPage);
    //console.log("endPage: ",endPage);

    let index = 0; // Track the current index in existing page items
    for (let i = startPage; i <= endPage; i++) {
      let pageItem;
      if (index < existingPageLinks.length) {
        //console.log("if: done");
        // Update an existing item
        pageItem = existingPageLinks[index];
        pageItem.querySelector(".page-link").innerText = i;
        pageItem.querySelector(".page-link").setAttribute("data-page", i);
      } else {
        //console.log("else: done");
        // Add a new item if needed
        pageItem = document.createElement("li");
        pageItem.className = "page-item";
        pageItem.innerHTML = `<a class="page-link" href="#" data-page="${i}">${i}</a>`;
        pagination.insertBefore(pageItem, pagination.querySelector("li:last-child"));
      }
      pageItem.querySelector(".page-link").classList.toggle("page-link-active", i === currentPage); // Set active class
      index++;
      //console.log("index: ",index);
    }

    // Remove any extra items beyond the new range
    /*while (index < existingPageLinks.length) {
        pagination.removeChild(existingPageLinks[index]);
        index++;
    }*/

    // Update Previous button
    const previousBtn = document.querySelector(".page-prev");
    previousBtn.classList.toggle("item-disabled", currentPage === 1);
    previousBtn.querySelector(".page-link").setAttribute("data-page", currentPage - 1);
    //console.log("previousBtn: ",previousBtn);
    // Update Next button
    const nextBtn = document.querySelector(".page-next");
    nextBtn.classList.toggle("item-disabled", currentPage === endPage);
    nextBtn.querySelector(".page-link").setAttribute("data-page", currentPage + 1);
    //console.log("nextBtn: ",nextBtn);
    // Update First button
    const firstBtn = document.querySelector(".page-first");
    firstBtn.querySelector(".page-link").setAttribute("data-page", 1);
    //console.log("firstBtn: ",firstBtn);
    // Update Last button
    const lastBtn = document.querySelector(".page-last");
    lastBtn.querySelector(".page-link").setAttribute("data-page", lastPage);
    //console.log("lastBtn: ",lastBtn);
    //update no of pages paragraph
    document.getElementById("page-total").innerHTML = "تم تحميل " + currentPage + " من اجمالي " + lastPage + " صفحات ";
  }


  // Example usage with API response
  //const response = { last_page: 10, page_no: 3 }; // Example data
  //updatePagination(response.last_page, response.page_no);

  // Event listener for page links
  document.querySelector(".pagination").addEventListener("click", function (event) {
    const target = event.target;
    if (target.classList.contains("page-link") &&
      !target.parentNode.classList.contains("disabled") &&
      !target.closest("#page-size")) {  // Ensures page-size is not part of the event
      event.preventDefault();
      const selectedPage = parseInt(target.getAttribute("data-page"), 10);
      const selectedPageSize = document.getElementById("page-size").value;

      if (lastPage) {
        return
      }

      // Fetch data for selected page
      console.log(`Fetching data for page: ${selectedPage}, with page size ${selectedPageSize}, for ${active_url}`);
      if (active_url == "server_filtered_data") {
        currentPage = selectedPage;
        applyFilters(selectedPage, selectedPageSize);
      } else {
        currentPage = selectedPage;
        fetchDataFromServer({ page: selectedPage, size: selectedPageSize });
      }
    }
  });


  // Event listener for page size change
  document.querySelector("#page-size").addEventListener("change", function () {
    const selectedPageSize = this.value;
    const selectedPage = document.querySelector(".page-link.page-link-active").innerHTML;

    //console.log(`Selected page size: ${selectedPageSize}`);
    console.log(`Fetching data for page: ${selectedPage}, with page size ${selectedPageSize}, for ${active_url}`);
    if (active_url == "server_filtered_data") {
      applyFilters(selectedPage, selectedPageSize);
    } else {
      fetchDataFromServer({ page: selectedPage, size: selectedPageSize });
    }
  });

  function showLoader() {
    const loader = document.getElementById("loader-element");
    loader.classList.remove("d-none"); // Show the loader by removing d-none
    loader.classList.add("d-flex"); // Ensure d-flex is applied for flexbox display
    //console.log("loader shown");
  }

  function hideLoader() {
    const loader = document.getElementById("loader-element");

    // Set a delay (e.g., 2000ms = 2 seconds)
    setTimeout(function () {
      loader.classList.remove("d-flex"); // Remove d-flex
      loader.classList.add("d-none"); // Hide the loader by adding d-none
      //console.log("loader hidden after delay");
    }, 3000); // 2000ms = 2 seconds delay
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
        //'Authorization': `Bearer ${jwtToken_access}`,
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

document.getElementById('add-main-btn').addEventListener('click', function () {
  const itemId = sessionStorage.getItem('pno');
  if (!itemId) {
    alert("الرجاء اختيار صنف برقم خاص");
    return
  }
  openWindow(`/item/${itemId}/add-more-categories`);
});

// const main_choices = new Choices("#item-main", {
//   removeItemButton: true,
//   searchEnabled: true,
//   placeholder: true, // Enable placeholder behavior
//   placeholderValue: "اختر بيان", // Custom placeholder text
//   noResultsText: "لا يوجد نتائج" // Custom message when no results match search
// });

// const sub_choices = new Choices("#item-sub-main", {
//   removeItemButton: true,
//   searchEnabled: true,
//   placeholder: true, // Enable placeholder behavior
//   placeholderValue: "اختر بيان", // Custom placeholder text
//   noResultsText: "لا يوجد نتائج" // Custom message when no results match search
// });

// const model_choices = new Choices("#model", {
//   removeItemButton: true,
//   searchEnabled: true,
//   placeholder: true, // Enable placeholder behavior
//   placeholderValue: "اختر بيان", // Custom placeholder text
//   noResultsText: "لا يوجد نتائج" // Custom message when no results match search
// });

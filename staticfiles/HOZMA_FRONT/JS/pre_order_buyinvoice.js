     
 const jwtToken_access = localStorage.getItem("session_data@access_token").replace(/"/g, '');
 /*const contextData = {
   data: JSON.parse("{{ data|escapejs }}"),
 };

 console.log(contextData.data);*/
 // Fetch client ID from the URL query string

 // Initialize Tabulator table
 const table = new Tabulator("#users-table", {
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
   data: [],//contextData.data, // Placeholder, will be loaded dynamically
   columns: [
           { title: "رقم الي", field: "autoid" ,visible:false},
           { title: "رقم الفاتورة", field: "invoice_no" },
           { title: "الرقم الاصلي", field: "original_no" },
           { title: "التاريخ", field: "invoice_date" },
           { title: "المصدر", field: "source" },
           { title: "سعر الفاتورة", field: "amount" },
           { title: "التخفيض", field: "discount" },
           { title: "صافي الفاتورة", field: "net_amount" },
           { title: "العملة", field: "currency" },
           { title: "سعر الصرف", field: "exchange_rate" },
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
function getCSRFToken() {
       const csrfInput = document.querySelector(
         "[name=csrfmiddlewaretoken]"
       );
       return csrfInput ? csrfInput.value : "";
}
let childWindows = [];
function openWindow(url,width = 600,height = 700) {
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
 table.on("rowClick", function (e, row) {
   console.log("Row clicked:", row.getData().autoid);
   const data = {
     id: row.getData().autoid,
   };
   console.log("sent id: ",data);

   // Make a POST request to the server
   customFetch("buy_invoice_add_items", {
     method: "POST",
     headers: {
       "Content-Type": "application/json",
       "X-CSRFToken": getCSRFToken(),
       'Authorization': `Bearer ${jwtToken_access}`,
     },
     body: JSON.stringify(data),
   })
     .then((response) => {
       // Check if the response is a redirect (3xx status code)
       if (response.redirected) {
         // Open the new URL in a new window/tab
         openWindow(response.url,1200,700);
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
 });
 //table.setData(contextData.data);
 ///////////

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
function fetchDataFromServer({ page = 1, size = 100 }) {
//if (isLoading) return; // Prevent fetch if already loading
//isLoading = true; // Set loading flag before initiating fetch

// Use the URL in your fetch request


console.time("fetchData"); // Start timer

customFetch(`fetch-buyinvoices?page=${page}&size=${size}`, {
     method: 'GET',
     headers: {
       'Content-Type': 'application/json',
       'Authorization': `Bearer ${jwtToken_access}`,  // 👈 Include JWT token
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

   document.getElementById("dinar-total").value = Number(data.total_amount).toLocaleString(undefined, { minimumFractionDigits: 2 }) + " د.ل";
   updateCalc();


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

// Debounce function definition
function debounce(func, wait) {
let timeout;
return function (...args) {
 clearTimeout(timeout);
 timeout = setTimeout(() => func.apply(this, args), wait);
};
}

// Apply debounce to applyFilters with a 300ms delay
//const debouncedApplyFilters = debounce(() => applyFilters(1), 390);
fetchDataFromServer({ page: 1, size: 100 });

 function showLoader() {
   const loader = document.getElementById("loader-element");
   loader.classList.remove("d-none"); // Show the loader by removing d-none
   loader.classList.add("d-flex"); // Ensure d-flex is applied for flexbox display
   //console.log("loader shown");
 }

 function hideLoader() {
   const loader = document.getElementById("loader-element");

   // Set a delay (e.g., 2000ms = 2 seconds)
   setTimeout(function() {
     loader.classList.remove("d-flex"); // Remove d-flex
     loader.classList.add("d-none"); // Hide the loader by adding d-none
     //console.log("loader hidden after delay");
   }, 3000); // 2000ms = 2 seconds delay
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
     document.getElementById("page-total").innerHTML = "تم تحميل "+ currentPage + " من اجمالي " + lastPage + " صفحات " ;
 }


 // Example usage with API response
 //const response = { last_page: 10, page_no: 3 }; // Example data
 //updatePagination(response.last_page, response.page_no);

 // Event listener for page links
 document.querySelector(".pagination").addEventListener("click", function (event) {
const target = event.target;
if (target.classList.contains("page-link") &&
   !target.parentNode.classList.contains("disabled") &&
   !target.closest("#page-size") ) {  // Ensures page-size is not part of the event
   event.preventDefault();
   const selectedPage = parseInt(target.getAttribute("data-page"), 10);
   const selectedPageSize = document.getElementById("page-size").value;

   if(lastPage){
     return
   }

   // Fetch data for selected page
   console.log(`Fetching data for page: ${selectedPage}, with page size ${selectedPageSize}, for ${active_url}`);
   if(active_url=="server_filtered_data"){
       currentPage = selectedPage;
       applyFilters(selectedPage,selectedPageSize);
   }else{
       currentPage = selectedPage;
       fetchDataFromServer({page: selectedPage,size: selectedPageSize});
   }
}
});


 // Event listener for page size change
 document.querySelector("#page-size").addEventListener("change", function () {
   const selectedPageSize = this.value;
   const selectedPage = document.querySelector(".page-link.page-link-active").innerHTML;

   //console.log(`Selected page size: ${selectedPageSize}`);
   console.log(`Fetching data for page: ${selectedPage}, with page size ${selectedPageSize}, for ${active_url}`);
   if(active_url=="server_filtered_data"){
       applyFilters(selectedPage,selectedPageSize);
   }else{
       fetchDataFromServer({page: selectedPage,size: selectedPageSize});
   }
 });

 function applyFilters(pageno = 1, pagesize = pageSize) {
     console.time("applyFiltersTime");
     // Helper function to get selected text from a dropdown
     function getSelectedText(selectId) {
       const select = document.getElementById(selectId);
       return select && select.selectedIndex !== 0
         ? select.options[select.selectedIndex].text
         : "";
     }

     // Helper function to get trimmed and lowercased input value
     function getInputValue(inputId) {
       const input = document.getElementById(inputId);
       return input ? input.value.trim().toLowerCase() : "";
     }

     // Capture filter values dynamically
     const filterValues = {
       source: getSelectedText("source"),
       fromdate: getInputValue("from-date"),
       todate: getInputValue("to-date"),
       invoice_no: getInputValue("invoice-autoid"),
       page: parseInt(pageno, 10) || 1,
       size: pagesize || 20,
     };

     console.log("Filter values:", filterValues);

     // Function to get CSRF token
     function getCSRFToken() {
       const csrfInput = document.querySelector(
         "[name=csrfmiddlewaretoken]"
       );
       return csrfInput ? csrfInput.value : "";
     }

     console.time("FilterTime");

     customFetch("filter_buyinvoices", {
       method: "POST",
       headers: {
         "Content-Type": "application/json",
         "X-CSRFToken": getCSRFToken(),
         'Authorization': `Bearer ${jwtToken_access}`,
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
         console.log("response: ",data);
         console.log("filter data",data.data);

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

         document.getElementById("dinar-total").value = data.total_amount + " دل ";
         updateCalc();

       })
       .catch((error) => {
         console.error("Error fetching filtered data:", error.message);
       })
       .finally(() => {
         console.timeEnd("FilterTime");
         console.timeEnd("applyFiltersTime");
         active_url="server_filtered_data";
         isLoading = false;
         hideLoader();
       });
   }

   // Add event listeners to all filter inputs
   const filterInputs = [
     "invoice-autoid",
     "source",
     "from-date",
     "to-date",
   ];

    function debounce(func, wait) {
       let timeout;
       return function(...args) {
           clearTimeout(timeout);
           timeout = setTimeout(() => func.apply(this, args), wait);
       };
   }

   // Apply debounce to applyFilters with a 300ms delay
   const debouncedApplyFilters = debounce(() => applyFilters(1,pageSize), 390);
   filterInputs.forEach((inputId) => {
     document
       .getElementById(inputId)
       .addEventListener("input", () => {
       debouncedApplyFilters();
   });
   });
   ///////////////////

   document
     .getElementById("clear-btn")
     .addEventListener("click", clearForm);
   function clearForm() {
     window.requestAnimationFrame(function () {
       const formElements = document.querySelectorAll(
         "form input, form select, form textarea"
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
       });

       if (table) {
         table.clearFilter(); // Clear all filters applied
         fetchDataFromServer({ page: 1, size: 100 });
       }
     });
   }
   function updateCalc(){
    const total_dinar_str = document.getElementById("dinar-total").value;
    const total_dinar = parseFloat(total_dinar_str.replace(/[٬, د.ل\s]/g, '')); // Remove commas, Arabic letters, and spaces
    
    const dinar_paid = parseFloat(document.getElementById("dinar-paid").value);
     // Assuming dinar_paid is another input field
     const number = total_dinar.replace(/[^\d.]/g, '');
     const total_amount = parseFloat(number);

     // Calculate the net amount
     const net_amount = total_amount - dinar_paid;

     // Format the net amount with commas and two decimal places
     const formatted_net_amount = new Intl.NumberFormat('en-US', {
         minimumFractionDigits: 2,
         maximumFractionDigits: 2
     }).format(net_amount);

     // Set the formatted value with "دل"
     document.getElementById("dinar-net").value = Number(formatted_net_amount).toLocaleString(undefined, { minimumFractionDigits: 2 }) + " د.ل";
    }
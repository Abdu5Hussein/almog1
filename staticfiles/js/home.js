document.addEventListener("DOMContentLoaded", function () {
    const menuToggle = document.getElementById("sidebar-toggler");
    const sidebar = document.getElementById("sidebar");
    // Add click event to toggle the nav links on mobile
    menuToggle.addEventListener("click", function () {
        console.log("toggle sidebar");
        console.log(sidebar);
        sidebar.classList.toggle("show"); // Toggle the 'show' class to display/hide the menu
    });


    // Toggle submenus
    document.querySelectorAll(".toggle-submenu").forEach((item) => {
        item.addEventListener("click", (event) => {
            event.preventDefault(); // Prevent default anchor behavior
            const submenu = item.nextElementSibling;

            // Close all other submenus
            document.querySelectorAll(".sub-menu").forEach((sub) => {
                if (sub !== submenu) {
                    sub.style.display = "none"; // Hide other submenus
                }
            });

            // Toggle the clicked submenu
            submenu.style.display =
                submenu.style.display === "block" ? "none" : "block";
        });
    });

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
    window.openWindow = openWindow; // Expose the function globally

    // Helper function to assign click events
    function assignClickEvent(elementId, url, windowName, width, height) {
        const element = document.getElementById(elementId);
        if (element) {
            element.onclick = function () {
                openWindow(url, windowName, width, height);
            };
        }
    }

    // Define menu items and their respective window properties
    const menuItems = [
        {
            id: "item-1-1",
            url: "/products-details",
            name: "productsDetails",
            width: 1100,
            height: 900,
        },
        {
            id: "item-1-2",
            url: "/products-reports",
            name: "productsReports",
            width: 1100,
            height: 700,
        },
        {
            id: "item-1-4",
            url: "/edit-prices",
            name: "editPrices",
            width: 1100,
            height: 700,
        },
        {
            id: "item-1-3",
            url: "/partial-products-reports",
            name: "partialProductsReports",
            width: 1100,
            height: 700,
        },
        {
            id: "item-1-5",
            url: "/products-movement",
            name: "products-movement",
            width: 1100,
            height: 700,
        },
        {
            id: "item-1-6",
            url: "/products-balance",
            name: "products-balance",
            width: 1100,
            height: 700,
        },
        {
            id: "item-1-7",
            url: "/data-inventory",
            name: "data-inventory",
            width: 1100,
            height: 700,
        },
        {
            id: "item-1-8",
            url: "/lost-and-damaged",
            name: "lost-and-damaged",
            width: 1100,
            height: 700,
        },
        {
            id: "item-1-9",
            url: "/storage",
            name: "storage",
            width: 1100,
            height: 500,
        },
        {
            id: "item-1-16",
            url: "/products/add-description",
            name: "add-description",
            width: 1100,
            height: 500,
        },
        {
            id: "item-7-1",
            url: "/clients-management",
            name: "clients-management",
            width: 1100,
            height: 700,
        },
        {
            id: "item-7-2",
            url: "/clients-reports",
            name: "clients-reports",
            width: 1100,
            height: 700,
        },
        {
            id: "item-9-1",
            url: "/storage-records",
            name: "storage-records",
            width: 1100,
            height: 700,
        },
        {
            id: "item-9-2",
            url: "/storage-reports",
            name: "storage-reports",
            width: 1100,
            height: 700,
        },
        {
            id: "item-2-1",
            url: "/add-buy-invoice?local=true",
            name: "add-buy-invoice-local",
            width: 1100,
            height: 700,
        },
        {
            id: "item-2-2",
            url: "/b_invoice_management?local=true",
            name: "b_invoice_management-local",
            width: 1100,
            height: 700,
        },
        {
            id: "item-2-3",
            url: "/buy-invoice_edit-prices?local=true",
            name: "buy-invoice_edit-prices-local",
            width: 1100,
            height: 700,
        },
        {
            id: "item-2-5",
            url: "/temp_confirm?local=true",
            name: "temp_confirm-local",
            width: 1100,
            height: 700,
        },
        {
            id: "item-3-1",
            url: "/add-buy-invoice",
            name: "add-buy-invoice",
            width: 1100,
            height: 700,
        },
        {
            id: "item-3-2",
            url: "/b_invoice_management",
            name: "b_invoice_management",
            width: 1100,
            height: 700,
        },
        {
            id: "item-3-3",
            url: "/buy-invoice_edit-prices",
            name: "buy-invoice_edit-prices",
            width: 1100,
            height: 700,
        },
        {
            id: "item-3-5",
            url: "/temp_confirm",
            name: "temp_confirm",
            width: 1100,
            height: 700,
        },
        {
            id: "item-5-1",
            url: "/sell_invoice_add_invoice",
            name: "sell_invoice_add_invoice",
            width: 1100,
            height: 700,
        },
        {
            id: "item-5-2",
            url: "/sell_invoice_management",
            name: "sell_invoice_management",
            width: 1100,
            height: 700,
        },
        {
            id: "item-5-4",
            url: "/sell_invoice_search_storage",
            name: "sell_invoice_search_storage",
            width: 1100,
            height: 700,
        },
        {
            id: "item-5-5",
            url: "/sell_invoice_storage_report",
            name: "sell_invoice_storage_report",
            width: 1100,
            height: 700,
        },
        {
            id: "item-6-1",
            url: "/sell-invoice/return-items-page/",
            name: "return-items/",
            width: 1100,
            height: 700,
        },
        {
            id: "item-6-2",
            url: "/sell-invoice/return-items-report/",
            name: "return-report/",
            width: 1100,
            height: 700,
        },
        {
            id: "item-15-1",
            url: "/buy-invoice/return-items-page/?buy_return=1",
            name: "buy-return-items/",
            width: 1100,
            height: 700,
        },
        {
            id: "item-15-2",
            url: "/buy-invoice/return-items-report/?buy_return=1",
            name: "buy-return-report/",
            width: 1100,
            height: 700,
        },
        {
            id: "item-9-3",
            url: "/clients/payment-requests",
            name: "payment-requests/",
            width: 1100,
            height: 700,
        },
        {
            id: "item-13-1",
            url: "/sources/management",
            name: "sources-management/",
            width: 1100,
            height: 700,
        },
        {
            id: "item-13-2",
            url: "/sources/report",
            name: "sources-report/",
            width: 1100,
            height: 700,
        },
        {
            id: "item-11-1",
            url: "/users/management",
            name: "users-management/",
            width: 1100,
            height: 700,
        },
        {
            id: "item-8-1",
            url: "/employees/management",
            name: "employees-management-details",
            width: 1100,
            height: 700,
        },
        {
            id: "item-8-3",
            url: "/employees/management/salaries",
            name: "employees-salaries/",
            width: 1100,
            height: 700,
        },
        {
            id: "item-8-4",
            url: "/employees/management/salaries/edit",
            name: "employees-salaries-edit/",
            width: 1100,
            height: 700,
        },
        {
            id: "item-8-5",
            url: "/employees/management/reports",
            name: "employees-reports/",
            width: 1100,
            height: 700,
        },
        {
            id: "item-8-6",
            url: "/employees/management/salaries/history",
            name: "employees-salaries-history/",
            width: 1100,
            height: 700,
        },
        {
            id: "item-8-7",
            url: "/employees/management/attendance",
            name: "employees-attendance-history/",
            width: 1100,
            height: 700,
        },
        {
            id: "item-14-1",
            url: "/print/dynamic-paper",
            name: "print-doc",
            width: 1100,
            height: 700,
        },
    ];

    // Assign click events for all menu items
    menuItems.forEach((item) => {
        assignClickEvent(item.id, item.url, item.name, item.width, item.height);
    });

    document.getElementById("logout-btn").addEventListener("click", function () {
        logoutFunction();
    });

    function logoutFunction() {
        fetch(`/api/user/logout`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
        })
            .then((response) => response.json())
            .then((result) => {
                console.log(result);
                console.log("Logged out successfully");

                // Redirect to login page
                window.location.href = "/login";
            })
            .catch((error) => {
                console.error("Error logging out:", error);
            });
    }

    //////analtytic and statistics

    async function loadAnalytics() {
        const response = await fetch("http://45.13.59.226/hozma/api/analytics/items/?period=300");
        const data = await response.json();

        // Inventory stats
        document.getElementById('totalItems').textContent = data.inventory_stats.total_items;
        document.getElementById('availableItems').textContent = data.inventory_stats.available_items;
        document.getElementById('outOfStock').textContent = data.inventory_stats.out_of_stock;
        document.getElementById('lowStock').textContent = data.inventory_stats.low_stock;

        /*// Sales Chart
        new Chart(document.getElementById('salesChart'), {
            type: 'line',
            data: {
                labels: data.sales_trends.map(s => new Date(s.day).toLocaleDateString('ar-EG')),
                datasets: [{
                    label: 'إجمالي المبيعات',
                    data: data.sales_trends.map(s => s.total_sales),
                    borderColor: '#0d6efd',
                    fill: false,
                    tension: 0.3
                }]
            },
            options: {
                plugins: { legend: { display: true } },
                responsive: true
            }
        });*/

        // Payment Methods (source_analysis)
        /*
        new Chart(document.getElementById('paymentMethodsChart'), {
            type: 'doughnut',
            data: {
                labels: data.source_analysis.map(s => s.buysource),
                datasets: [{
                    data: data.source_analysis.map(s => s.total_sales),
                    backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#28a745', '#6f42c1']
                }]
            }
        });

        // Categories chart
        new Chart(document.getElementById('categoriesChart'), {
            type: 'bar',
            data: {
                labels: data.categories.map(c => c.itemmain || 'غير معروف'),
                datasets: [{
                    label: 'عدد العناصر',
                    data: data.categories.map(c => c.count),
                    backgroundColor: '#198754'
                }]
            }
        });

        // Price Ranges
        new Chart(document.getElementById('priceRangeChart'), {
            type: 'pie',
            data: {
                labels: data.price_ranges.map(p => p.price_range),
                datasets: [{
                    data: data.price_ranges.map(p => p.count),
                    backgroundColor: ['#ffc107', '#dc3545', '#17a2b8', '#6610f2', '#20c997']
                }]
            }
        });*/

        // Top Products
        const topList = document.getElementById("topProductsList");
        topList.innerHTML = ""; // Clear existing list
        data.top_items.forEach(item => {
            const li = document.createElement("div");
            li.className = "list-group-item d-flex align-items-center";
            li.innerHTML = `
            <div class="flex-grow-1">
                <h6 class="mb-1">${item.itemname}</h6>
                <small class="text-muted">تم بيع ${item.total_sales} قطعة</small>
            </div>
            <span class="badge bg-primary rounded-pill">${item.total_sales}</span>
        `;
            topList.appendChild(li);
        });

        // Recent Orders Chart (bar chart horizontal)
        const recentOrders = data.recent_orders;
        const itemLabels = recentOrders.map(item => item.itemname);
        const buyPrices = recentOrders.map(item => item.buyprice);
        const buySources = recentOrders.map(item => item.buysource);

        /*const ctx = document.getElementById("recentOrdersChart").getContext("2d");

        new Chart(ctx, {
            type: "bar",
            data: {
                labels: itemLabels,
                datasets: [{
                    label: "سعر الشراء",
                    data: buyPrices,
                    backgroundColor: "rgba(54, 162, 235, 0.7)",
                    borderColor: "rgba(54, 162, 235, 1)",
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                indexAxis: 'y',
                plugins: {
                    tooltip: {
                        callbacks: {
                            afterLabel: function(context) {
                                return "المصدر: " + buySources[context.dataIndex];
                            }
                        }
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: "السعر"
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: "المنتج"
                        }
                    }
                }
            }
        });*/
    }

    loadAnalytics();


    // Fetch top products
    /*customFetch('http://45.13.59.226/hozma/api/top-products/')
      .then(response => response.json())
      .then(data => {
        const topProductsList = document.getElementById('topProductsList');
        data.products.forEach(product => {
            const item = document.createElement('li');
            item.className = 'list-group-item d-flex justify-content-between align-items-center';
            item.innerHTML = `
                ${product.name}
                <span class="badge bg-primary rounded-pill">${product.sales} مبيعاً</span>
            `;
            topProductsList.appendChild(item);
        });
    });*/

    // Example JavaScript for form submission
    /* document.getElementById('productForm').addEventListener('submit', function(e) {
         e.preventDefault();
         document.getElementById('successAlert').style.display = 'block';
         setTimeout(function() {
             document.getElementById('successAlert').style.display = 'none';
         }, 3000);
     });*/

    customFetch("http://45.13.59.226/hozma/api/preorders/")
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById("preordersBody");

            // Get the last 4 preorders
            const preorders = data.preorders.slice(-4).reverse(); // To show newest at top

            preorders.forEach(order => {
                const row = document.createElement("tr");

                row.innerHTML = `
  <td>${order.invoice_no.toString()}</td>

  <td>${order.client_name}</td>
  <td>${new Date(order.date_time).toLocaleDateString('en-UK')}</td>
  <td>${parseFloat(order.amount).toLocaleString('en-US')} د٫ل</td>
  <td>
    <span class="badge bg-warning text-dark">${order.invoice_status}</span></td>
     <td>
        <span class="badge ${order.shop_confrim ? 'bg-success' : 'bg-danger'}">
      ${order.shop_confrim ? 'تم التأكيد' : 'غير مؤكد'}
    </span>
  </td>
  <td><a href="/hozma/preorder-detail/${order.invoice_no}/" class="btn btn-sm btn-edit">التفاصيل</a></td>
`;

                tbody.appendChild(row);
            });
        })
        .catch(error => {
            console.error("Failed to load preorders:", error);
        });

    customFetch('http://45.13.59.226/hozma/api/invoice-summary/')
        .then(response => response.json())
        .then(data => {
            const totalAmount = data.total_amount.toLocaleString('EN-UK', { style: 'currency', currency: 'LYD' });
            const changeRate = data.change_rate;

            // Update the amount
            document.getElementById('total-amount').textContent = totalAmount;

            // Update the change rate
            const rateElement = document.getElementById('change-rate');
            rateElement.innerHTML = `
                <i class="fas ${changeRate >= 0 ? 'fa-caret-up text-success' : 'fa-caret-down text-danger'}"></i>
                ${Math.abs(changeRate)}%
            `;
        })
        .catch(error => {
            console.error('Error fetching invoice summary:', error);
            document.getElementById('total-amount').textContent = 'خطأ في التحميل';
            document.getElementById('change-rate').textContent = '';
        });



    customFetch('http://45.13.59.226/hozma/api/invoice-stats/')  // Replace with your actual API endpoint
        .then(res => res.json())
        .then(data => {
            // Update the number of new orders
            document.getElementById('new-orders-count').textContent = data.new_unconfirmed_orders_today;
            // Update the shop confirmed count and set active color
            document.getElementById('shop-confirmed-count').textContent = 'تم تأكيدها من قبل المتجر: ' + data.shop_confirmed_this_month;
            let confirmedStatusElement = document.getElementById('shop-confirmed-count');
            if (data.shop_confirmed_this_month > 0) {
                confirmedStatusElement.classList.remove('text-danger');
                confirmedStatusElement.classList.add('text-success'); // Green color for confirmed
            } else {
                confirmedStatusElement.classList.remove('text-success');
                confirmedStatusElement.classList.add('text-danger'); // Red color for unconfirmed
            }

            // Update the total invoice count
            document.getElementById('current-month-invoice-count').textContent = 'إجمالي الفواتير: ' + data.current_month_invoice_count;

            // Update the percentage increase from last week
            document.getElementById('percentage-increase').textContent = data.percentage_increase + '%';
        })
        .catch(err => console.error("Error loading stats:", err));

    // Fetch inventory data
    /*customFetch('http://45.13.59.226/hozma/api/inventory/')
      .then(response => response.json())
      .then(data => {
        const inventoryTable = document.getElementById('inventoryTable');

        data.products.forEach(product => {
            const row = document.createElement('tr');

            // Determine stock status
            let statusBadge = '';
            if(product.quantity > 10) {
                statusBadge = '<span class="badge bg-success">متوفر</span>';
            } else if(product.quantity > 0) {
                statusBadge = '<span class="badge bg-warning text-dark">كمية محدودة</span>';
            } else {
                statusBadge = '<span class="badge bg-danger">نفذ من المخزون</span>';
            }

            row.innerHTML = `
                <td><img src="${product.image || 'https://via.placeholder.com/50'}" width="50"></td>
                <td>${product.name}</td>
                <td>${product.price.toLocaleString()} د.ل</td>
                <td>${product.quantity}</td>
                <td>${statusBadge}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary me-1"><i class="fas fa-edit"></i></button>
                    <button class="btn btn-sm btn-outline-danger"><i class="fas fa-trash"></i></button>
                </td>
            `;

            inventoryTable.appendChild(row);
        });
    });*/
    // Fetch sales trends and top items


    // Fetch data from API
    fetch('http://45.13.59.226/hozma/api/sales-analysis/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(apiData => {
            // Process monthly sales data
            const arabicMonths = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'];
            const monthlySales = apiData.monthly_sales
                .filter(item => item.month !== null)
                .map(item => {
                    const date = new Date(item.month);
                    return {
                        month: arabicMonths[date.getMonth()] + ' ' + date.getFullYear(),
                        sales: item.total_sales
                    };
                });

            // Create Monthly Sales Chart
            const salesCtx = document.getElementById('salesChart1').getContext('2d');
            const salesChart = new Chart(salesCtx, {
                type: 'bar',
                data: {
                    labels: monthlySales.map(item => item.month),
                    datasets: [{
                        label: 'إجمالي المبيعات',
                        data: monthlySales.map(item => item.sales),
                        backgroundColor: 'rgba(54, 162, 235, 0.6)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1,
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            rtl: true,
                            callbacks: {
                                label: function (context) {
                                    return 'المبلغ: ' + context.raw.toLocaleString('en-UK') + 'د٫ل';
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function (value) {
                                    return value.toLocaleString('en-UK') + 'د٫ل';
                                }
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });

            // Process top clients data (take top 5)
            const topClients = apiData.top_clients.slice(0, 5);

            // Create Top Clients Chart
            const clientsCtx = document.getElementById('clientsChart').getContext('2d');
            const clientsChart = new Chart(clientsCtx, {
                type: 'doughnut',
                data: {
                    labels: topClients.map(client => client.client_name),
                    datasets: [{
                        data: topClients.map(client => client.total_purchase),
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.7)',
                            'rgba(54, 162, 235, 0.7)',
                            'rgba(255, 206, 86, 0.7)',
                            'rgba(75, 192, 192, 0.7)',
                            'rgba(153, 102, 255, 0.7)'
                        ],
                        borderColor: [
                            'rgba(255, 99, 132, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(153, 102, 255, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'left',
                            rtl: true
                        },
                        tooltip: {
                            rtl: true,
                            callbacks: {
                                label: function (context) {
                                    return context.label + ': ' + context.raw.toLocaleString('en-UK') + 'د٫ل';
                                }
                            }
                        }
                    },
                    cutout: '70%'
                }
            });

            // Populate Top Items Table
            const topItemsTable = document.getElementById('topItemsTable');
            // Clear any existing rows first
            topItemsTable.innerHTML = '';
            apiData.top_items.forEach((item, index) => {
                const row = document.createElement('tr');
                row.innerHTML = `
                        <td>${index + 1}</td>
                        <td>${item.name}</td>
                        <td>${item.company || 'غير محدد'}</td>
                        <td>${item.total_quantity}</td>
                        <td>${item.total_price.toLocaleString('en-UK')} د.ل</td>
                    `;
                topItemsTable.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            // You might want to display an error message to the user here
            alert('حدث خطأ أثناء جلب البيانات. يرجى المحاولة مرة أخرى لاحقاً.');
        });



    fetch('http://45.13.59.226/hozma/api/purchase-analysis/')
        .then(response => response.json())
        .then(apiData => {
            // Arabic months
            const arabicMonths = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'];

            // Monthly purchases
            const monthlyPurchases = apiData.monthly_purchases
                .filter(item => item.month !== null)
                .map(item => {
                    const date = new Date(item.month);
                    return {
                        month: arabicMonths[date.getMonth()] + ' ' + date.getFullYear(),
                        amount: item.total_purchased
                    };
                });

            // Draw Monthly Purchases Chart
            const monthlyPurchasesCtx = document.getElementById('monthlyPurchasesChart').getContext('2d');
            new Chart(monthlyPurchasesCtx, {
                type: 'line',
                data: {
                    labels: monthlyPurchases.map(item => item.month),
                    datasets: [{
                        label: 'إجمالي المشتريات',
                        data: monthlyPurchases.map(item => item.amount),
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 2,
                        tension: 0.1,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            rtl: true,
                            callbacks: {
                                label: context => 'المبلغ: ' + context.raw.toLocaleString('en-UK') + 'د٫ل'
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            ticks: {
                                callback: value => value.toLocaleString('en-UK') + 'د٫ل'
                            }
                        },
                        x: { grid: { display: false } }
                    }
                }
            });

            // Top Vendors
            const topVendors = apiData.top_vendors
                .filter(vendor => vendor.source !== null && vendor.total_purchase > 0)
                .slice(0, 5);

            const vendorsCtx = document.getElementById('vendorsChart').getContext('2d');
            new Chart(vendorsCtx, {
                type: 'bar',
                data: {
                    labels: topVendors.map(v => v.source_obj__name || v.source),
                    datasets: [{
                        label: 'إجمالي المشتريات',
                        data: topVendors.map(v => v.total_purchase),
                        backgroundColor: 'rgba(153, 102, 255, 0.6)',
                        borderColor: 'rgba(153, 102, 255, 1)',
                        borderWidth: 1,
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            rtl: true,
                            callbacks: {
                                label: context => 'المبلغ: ' + context.raw.toLocaleString('en-UK') + 'د٫ل'
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: value => value.toLocaleString('en-UK') + 'د٫ل'
                            }
                        },
                        x: { grid: { display: false } }
                    }
                }
            });

            // Purchased Items Table
            const purchasedItemsTable = document.getElementById('purchasedItemsTable');
            apiData.top_purchased_items.forEach((item, index) => {
                const row = document.createElement('tr');
                const totalPrice = item.total_price || 0;
                const totalCost = item.total_cost || 0;
                const profit = totalPrice - totalCost;

                let profitMargin = 0;
                if (totalCost > 0) profitMargin = ((profit) / totalCost) * 100;
                else if (totalPrice > 0) profitMargin = 100;

                let profitClass = 'profit-neutral';
                if (profit > 0) profitClass = 'profit-positive';
                else if (profit < 0) profitClass = 'profit-negative';

                row.innerHTML = `
                    <td>${index + 1}</td>
                    <td>${item.name}</td>
                    <td>${item.company || 'غير محدد'}</td>
                    <td>${item.total_quantity}</td>
                    <td>${totalPrice.toLocaleString('en-UK')} د.ل</td>
                    <td>${totalCost.toLocaleString('en-UK')} د.ل</td>
                    <td class="${profitClass}">${profit.toLocaleString('en-UK')} د.ل</td>
                    <td class="${profitClass}">${profitMargin.toFixed(2)}%</td>
                `;
                purchasedItemsTable.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error fetching purchase analysis:', error);
        });
});



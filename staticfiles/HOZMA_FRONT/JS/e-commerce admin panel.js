async function loadAnalytics() {
    const response = await fetch("http://45.13.59.226/hozma/api/analytics/items/?period=300");
    const data = await response.json();

    // Inventory stats
    document.getElementById('totalItems').textContent = data.inventory_stats.total_items;
    document.getElementById('availableItems').textContent = data.inventory_stats.available_items;
    document.getElementById('outOfStock').textContent = data.inventory_stats.out_of_stock;
    document.getElementById('lowStock').textContent = data.inventory_stats.low_stock;

    // Sales Chart
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
    });

    // Payment Methods (source_analysis)
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
    });

    // Top Products
    const topList = document.getElementById("topProductsList");
    topList.innerHTML = ""; // Clear existing list
    data.top_items.forEach(item => {
        const li = document.createElement("div");
        li.className = "list-group-item d-flex align-items-center";
        li.innerHTML = `
            <img src="https://via.placeholder.com/40" class="rounded me-3" alt="Product">
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

    const ctx = document.getElementById("recentOrdersChart").getContext("2d");

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
    });
}

loadAnalytics();


// Fetch top products
customFetch('http://45.13.59.226/hozma/api/top-products/')
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
    });
 
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


        document.addEventListener("DOMContentLoaded", function () {
    customFetch('http://45.13.59.226/hozma/api/invoice-stats/')  // Replace with your actual API endpoint
        .then(res => res.json())
        .then(data => {
            // Update the number of new orders
            document.getElementById('new-orders-count1').textContent = data.new_unconfirmed_orders_today;
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
});
// Fetch inventory data
customFetch('http://45.13.59.226/hozma/api/inventory/')
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
    });
// Fetch sales trends and top items


document.addEventListener('DOMContentLoaded', function() {
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
                                    label: function(context) {
                                        return 'المبلغ: ' + context.raw.toLocaleString('en-UK') + 'د٫ل';
                                    }
                                }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    callback: function(value) {
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
                                    label: function(context) {
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
                        <td>${item.total_price.toLocaleString('en-UK')} ر.س</td>
                    `;
                    topItemsTable.appendChild(row);
                });
            })
            .catch(error => {
                console.error('Error fetching data:', error);
                // You might want to display an error message to the user here
                alert('حدث خطأ أثناء جلب البيانات. يرجى المحاولة مرة أخرى لاحقاً.');
            });
    });


    document.addEventListener('DOMContentLoaded', function () {
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
                    <td>${totalPrice.toLocaleString('en-UK')} ر.س</td>
                    <td>${totalCost.toLocaleString('en-UK')} ر.س</td>
                    <td class="${profitClass}">${profit.toLocaleString('en-UK')} ر.س</td>
                    <td class="${profitClass}">${profitMargin.toFixed(2)}%</td>
                `;
                purchasedItemsTable.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error fetching purchase analysis:', error);
        });
});

document.addEventListener('DOMContentLoaded', function () {
    try {
        const username = localStorage.getItem("session_data@EMPname");
        const email = localStorage.getItem("session_data@EMPusername"); // optional if you store it

        const nameElement = document.getElementById('userNamePlaceholder');
        const emailElement = document.getElementById('userEmailPlaceholder');

        if (username) {
            nameElement.textContent = username;
            if (email) {
                emailElement.textContent = email;
            }
        } else {
            nameElement.textContent = "حسابي";
            emailElement.textContent = "غير معروف";
            alert("No user data found. Please log in.");
        }
    } catch (e) {
        console.error('Error accessing localStorage:', e);
    }
});


document.addEventListener('DOMContentLoaded', async () => {
    const raw = localStorage.getItem('session_data@emp_id');
    if (!raw) return;
  
    const employeeId = raw.replace(/"/g, '');
  
    try {
      const res = await fetch(`/hozma/employees/${employeeId}/get-image/`, {
        credentials: 'include',
        headers: { 'Accept': 'application/json' }
      });
  
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const { employee_image } = await res.json();
  
      const defaultImage = '/static/HOZMA_FRONT/images/default-profile.png';
      const finalImage = employee_image
        ? (employee_image.startsWith('http') ? employee_image : `${window.location.origin}${employee_image}`)
        : defaultImage;
  
      // Set both image sources
      const img1 = document.getElementById('employee-profile-image');
      const img2 = document.getElementById('employee-profile-image-profile');
      if (img1) img1.src = finalImage;
      if (img2) img2.src = finalImage;
  
    } catch (err) {
      console.error('Error loading employee image:', err);
    }
  });

  document.getElementById("logout-btn").addEventListener("click", function (){
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
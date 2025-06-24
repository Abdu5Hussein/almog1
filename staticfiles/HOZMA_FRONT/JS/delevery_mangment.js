$(document).ready(function() {
    const invoiceNo = window.location.pathname.split('/').filter(Boolean).pop();
    let selectedDriver = null;
    let currentAssignedDriver = null;
    const modal = new bootstrap.Modal(document.getElementById('confirmationModal'));

    // Load order and driver data
    async function loadData() {
        try {
            // First get order details
            const orderResponse = await $.ajax({
                url: `/hozma/assign-driver/${invoiceNo}/`,
                method: 'GET',
                beforeSend: function(xhr) {
                    xhr.setRequestHeader("Authorization", "Bearer " + localStorage.getItem('access_token'));
                }
            });
            
            updateOrderInfo(orderResponse.order);
            
            // If order has an assigned driver, fetch their details
            if (orderResponse.order.assigned_employee) {
                const driverDetails = await getDriverDetails(orderResponse.order.assigned_employee);
                if (driverDetails) {
                    currentAssignedDriver = driverDetails;
                    updateCurrentAssignment(driverDetails);
                }
            }
            const driversResponse = await $.ajax({
                url: `/hozma/assign-driver/${invoiceNo}/`,
                method: 'GET',
                beforeSend: function(xhr) {
                    xhr.setRequestHeader("Authorization", "Bearer " + localStorage.getItem('access_token'));
                }
            });
            // Get available drivers
          
            
            updateAvailableDrivers(driversResponse.available_drivers);
            
        } catch (error) {
            handleAjaxError(error);
        }
    }

    // Fetch driver details from API
    async function getDriverDetails(driverId) {
        try {
            const response = await $.ajax({
                url: `/api/employees/${driverId}/`,
                method: 'GET',
                beforeSend: function(xhr) {
                    xhr.setRequestHeader("Authorization", "Bearer " + localStorage.getItem('access_token'));
                }
            });
            
            return {
                id: response.employee_id,
                name: response.name,
                phone: response.phone,
                status: response.is_available ? 'available' : 'unavailable',
                image: response.employee_image,
                type: response.type,
                vehicle: response.vehicle_type || 'غير معروف'
            };
            
        } catch (error) {
            console.error('Error fetching driver details:', error);
            return null;
        }
    }

    function updateOrderInfo(order) {
        $('#orderInfo').html(`
            <table class="table table-borderless">
                <tr><td><strong>العميل</strong></td><td>${order.client_name}</td></tr>
                <tr><td><strong>فاتورة رقم</strong></td><td>${order.invoice_no}</td></tr>
                <tr><td><strong>الحالة</strong></td><td><span class="badge rounded-pill bg-primary">${order.invoice_status}</span></td></tr>
                <tr>
                    <td><strong>التوصيل</strong></td>
                    <td>
                        <span class="status-badge ${getDeliveryStatusClass(order.delivery_status)}">
                            <i class="bi ${getDeliveryStatusIcon(order.delivery_status)}"></i>
                            ${formatDeliveryStatus(order.delivery_status)}
                        </span>
                    </td>
                </tr>
            </table>
        `);

        $('#orderStatusBadge')
            .removeClass()
            .addClass(`status-badge ${getDeliveryStatusClass(order.delivery_status)}`)
            .html(`<i class="bi ${getDeliveryStatusIcon(order.delivery_status)}"></i> ${formatDeliveryStatus(order.delivery_status)}`);
    }

    function updateCurrentAssignment(driver) {
        const container = $('#currentAssignmentContainer');
        const assignmentDiv = $('#currentAssignment');
        const banner = $('#assignmentBanner');

        container.show();
        banner.show();
        
        assignmentDiv.html(`
            <div class="d-flex align-items-center">
                ${driver.image ? `
                    <img src="${driver.image}" class="avatar me-3">
                ` : `
                    <div class="avatar avatar-initials me-3">
                        ${getInitials(driver.name)}
                    </div>
                `}
                <div>
                    <h5 class="mb-1">${driver.name}</h5>
                    <p class="text-muted mb-1"><i class="bi bi-telephone"></i> ${driver.phone}</p>
                    <div class="d-flex align-items-center">
                        <span class="badge ${driver.status === 'available' ? 'bg-success' : 'bg-warning'} me-2">
                            ${driver.status === 'available' ? 'متاح' : 'غير متاح'}
                        </span>
                        <span class="badge bg-info">${driver.type}</span>
                    </div>
                </div>
            </div>
            <div class="mt-3">
                <button class="btn btn-sm btn-outline-primary me-2" onclick="callDriver('${driver.phone}')">
                    <i class="bi bi-telephone"></i> اتصل بالسائق
                </button>
                <button class="btn btn-sm btn-outline-secondary" onclick="trackDriver(${invoiceNo})">
                    <i class="bi bi-map"></i> تتبع التوصيل
                </button>
            </div>
        `);
    }

    function updateAvailableDrivers(drivers) {
        const container = $('#driversContainer');
        const noDriversMessage = $('#noDriversMessage');

        if (drivers.length === 0) {
            container.hide();
            noDriversMessage.show();
            return;
        }

        noDriversMessage.hide();
        container.empty().show();

        drivers.forEach(driver => {
            const isAssignedDriver = currentAssignedDriver && driver.employee_id === currentAssignedDriver.id;
            
            container.append(`
                <div class="col-md-6 mb-3">
                    <div class="card driver-card p-3 ${isAssignedDriver ? 'assigned' : ''}" 
                         data-driver-id="${driver.employee_id}">
                        <div class="d-flex align-items-center">
                            ${driver.employee_image ? `
                                <img src="${driver.employee_image}" class="avatar me-3">
                            ` : `
                                <div class="avatar avatar-initials me-3">
                                    ${getInitials(driver.name)}
                                </div>
                            `}
                            <div class="flex-grow-1">
                                <h5 class="mb-1">${driver.name}</h5>
                                <p class="text-muted mb-1"><i class="bi bi-telephone"></i> ${driver.phone}</p>
                                ${isAssignedDriver ? 
                                    `<span class="badge bg-info">السائق الحالي</span>` : 
                                    `<span class="badge bg-success">متاح</span>`}
                            </div>
                            <button class="btn btn-sm ${isAssignedDriver ? 'btn-reassign' : 'btn-assign'} select-driver-btn">
                                <i class="bi ${isAssignedDriver ? 'bi-arrow-repeat' : 'bi-person-plus'}"></i> 
                                ${isAssignedDriver ? 'إعادة تعيين' : 'اختيار'}
                            </button>
                        </div>
                    </div>
                </div>
            `);
        });

        $('.select-driver-btn').click(function() {
            const card = $(this).closest('.driver-card');
            const driverId = card.data('driver-id');
            const driverName = card.find('h5').text();
            const driverPhone = card.find('.text-muted').text().replace('📱 ', '');
            const isReassign = card.hasClass('assigned');

            $('.driver-card').removeClass('selected');
            card.addClass('selected');

            selectedDriver = { id: driverId, name: driverName, phone: driverPhone };
            $('#driverName').text(driverName);
            $('#driverPhone').text(driverPhone);
            
            // Update modal for reassignment
            if (isReassign) {
                $('#modalTitle').html('<i class="bi bi-arrow-repeat me-2"></i> تأكيد إعادة التعيين');
                $('#reassignWarning').show();
            } else {
                $('#modalTitle').html('<i class="bi bi-person-check me-2"></i> تأكيد التعيين');
                $('#reassignWarning').hide();
            }
            
            modal.show();
        });
    }

    // Handle reassign button in banner
    $('#reassignBtn').click(function() {
        if (currentAssignedDriver) {
            const assignedDriverCard = $(`.driver-card[data-driver-id="${currentAssignedDriver.id}"]`);
            if (assignedDriverCard.length) {
                assignedDriverCard.find('.select-driver-btn').click();
            }
        }
    });

    $('#confirmAssignment').click(function() {
        const btn = $(this);
        btn.prop('disabled', true).html(`
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            جاري التعيين...
        `);

        $.ajax({
            url: `/hozma/assign-driver/${invoiceNo}/assign/`,
            method: 'POST',
            headers: {
                "X-CSRFToken": getCookie('csrftoken'),
                "Authorization": "Bearer " + localStorage.getItem('access_token')
            },
            data: { driver_id: selectedDriver.id },
            success: function(response) {
                modal.hide();
                showToast('success', `تم تعيين الطلب إلى ${selectedDriver.name}`);
                loadData(); // Refresh the data
            },
            error: function(xhr) {
                let errorMsg = 'فشل في تعيين السائق';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMsg = xhr.responseJSON.error;
                }
                showToast('error', errorMsg);
            },
            complete: function() {
                btn.prop('disabled', false).html(`
                    <i class="bi bi-check-circle me-2"></i> تأكيد التعيين
                `);
            }
        });
    });

    $('#driverSearch').on('input', function() {
        const searchTerm = $(this).val().toLowerCase();
        $('.driver-card').each(function() {
            const card = $(this);
            const driverName = card.find('h5').text().toLowerCase();
            const driverPhone = card.find('.text-muted').text().toLowerCase();

            card.closest('.col-md-6').toggle(driverName.includes(searchTerm) || driverPhone.includes(searchTerm));
        });
    });

    function getDeliveryStatusClass(status) {
        switch (status) {
            case 'not_assigned': return 'badge-not-assigned';
            case 'assigned': return 'badge-assigned';
            case 'delivered': return 'badge-delivered';
            default: return 'badge-pending';
        }
    }

    function getDeliveryStatusIcon(status) {
        switch (status) {
            case 'not_assigned': return 'bi-x-circle';
            case 'assigned': return 'bi-person-check';
            case 'delivered': return 'bi-check-circle';
            default: return 'bi-clock';
        }
    }

    function formatDeliveryStatus(status) {
        const statusMap = {
            'not_assigned': 'غير معين',
            'assigned': 'تم التعيين',
            'delivered': 'تم التوصيل',
            'pending': 'قيد الانتظار'
        };
        return statusMap[status] || status;
    }

    function getInitials(name) {
        return name.split(' ').map(part => part.charAt(0).toUpperCase()).join('');
    }

    function callDriver(phoneNumber) {
        window.location.href = `tel:${phoneNumber}`;
    }

    function trackDriver(orderId) {
        console.log(`Tracking order ${orderId}`);
        // Implement your tracking functionality here
        // window.location.href = `/tracking/${orderId}/`;
    }

    function handleAjaxError(xhr) {
        if (xhr.status === 404) {
            $('#orderInfo').html(`
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-octagon"></i> الطلب غير موجود
                </div>
            `);
        } else if (xhr.status === 401) {
            window.location.href = '/login/';
        } else {
            $('#orderInfo').html(`
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-octagon"></i> خطأ في تحميل البيانات
                </div>
            `);
        }
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function showToast(type, message) {
        // Implement your toast notification system here
        console.log(`${type.toUpperCase()}: ${message}`);
        alert(`${type.toUpperCase()}: ${message}`);
    }

    // Initial load
    loadData();
});
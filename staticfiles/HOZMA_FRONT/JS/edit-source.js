$(document).ready(function() {
    // Load all sources when page loads
    loadSources();
    
    // Handle form submission
    $('#edit-source-form').on('submit', function(e) {
        e.preventDefault();
        updateSourceInfo();
    });
});

// Fetch all sources and display them in the table
async function loadSources() {
    try {
        const response = await customFetch('/hozma/api/show_all_sources/');
        const data = await response.json();
        const tableBody = $('#source-table-body');
        tableBody.empty();
        
        if (data.length === 0) {
            tableBody.append(`
                <tr>
                    <td colspan="5" class="empty-state">
                        <i class="fas fa-box-open"></i>
                        <p>لا توجد مصادر متاحة</p>
                    </td>
                </tr>
            `);
            return;
        }
        
        data.forEach(source => {
            const row = `
                <tr>
                    <td>${source.name || 'غير متوفر'}</td>
                    <td>${source.email || 'غير متوفر'}</td>
                    <td>${source.phone || 'غير متوفر'}</td>
                    <td>
                        <button class="btn btn-edit" onclick="fetchSourceDetails(${source.clientid})">
                            <i class="fas fa-edit me-1"></i> تعديل
                        </button>
                    </td>
                    <td>
                        <a href="/hozma/products/add/${source.clientid}/" class="btn btn-add">
                            <i class="fas fa-plus me-1"></i> إضافة
                        </a>
                    </td>
                </tr>
            `;
            tableBody.append(row);
        });
    } catch (error) {
        console.error("Error loading sources:", error);
        $('#source-table-body').html(`
            <tr>
                <td colspan="5" class="error-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>حدث خطأ في تحميل المصادر</p>
                    <button class="btn btn-edit mt-2" onclick="loadSources()">
                        <i class="fas fa-sync-alt me-1"></i> إعادة المحاولة
                    </button>
                </td>
            </tr>
        `);
    }
}

// Fetch and display source details in the edit form
async function fetchSourceDetails(id) {
    try {
        const response = await customFetch(`/hozma/api/show_source_details/${id}/`);
        const data = await response.json();
        
        // Populate form fields
        $('#source-id').val(id);
        $('#name').val(data.name || '');
        $('#address').val(data.address || '');
        $('#email').val(data.email || '');
        $('#website').val(data.website || '');
        $('#phone').val(data.phone || '');
        $('#mobile').val(data.mobile || '');
        $('#commission').val(data.commission || '');
        $('#client_stop').prop('checked', data.client_stop || false);
        $('#curr_flag').prop('checked', data.curr_flag || false);
        
        // Show the edit form
        $('#edit-form-card').show();
        $('html, body').animate({
            scrollTop: $('#edit-form-card').offset().top
        }, 500);
        
    } catch (error) {
        console.error("Error fetching source details:", error);
        showAlert('حدث خطأ في جلب بيانات المصدر', 'error');
    }
}

// Update source information
async function updateSourceInfo() {
    const sourceId = $('#source-id').val();

    const data = {
        name: $('#name').val(),
        email: $('#email').val(),
        address: $('#address').val(),
        website: $('#website').val(),
        phone: $('#phone').val(),
        mobile: $('#mobile').val(),
        commission: $('#commission').val(),
        client_stop: $('#client_stop').is(':checked'),
        curr_flag: $('#curr_flag').is(':checked')
    };

    try {
        const response = await customFetch(`/hozma/api/edit_source_info/${sourceId}/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            showAlert('تم تحديث المصدر بنجاح', 'success');
            loadSources();  // Refresh table
            $('#edit-form-card').hide();
        } else {
            showAlert(`فشل في تحديث البيانات: ${JSON.stringify(result)}`, 'error');
        }
    } catch (error) {
        console.error("Error updating source:", error);
        showAlert('حدث خطأ أثناء تحديث البيانات', 'error');
    }
}

// Show alert message
function showAlert(message, type) {
    const alertDiv = $('#alertMessage');
    alertDiv.text(message);
    alertDiv.removeClass('alert-success alert-error').addClass(`alert-${type === 'success' ? 'success' : 'error'}`);
    alertDiv.fadeIn();
    
    setTimeout(() => {
        alertDiv.fadeOut();
    }, 5000);
}
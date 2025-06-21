
document.addEventListener('DOMContentLoaded', function () {
    const deleteForms = document.querySelectorAll('.delete-form');
    const successMessageDiv = document.getElementById('success-message');

    deleteForms.forEach(form => {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const deleteId = this.querySelector('input[name="delete-id"]').value;
            const csrfToken = '{{ csrf_token }}';
            const row = this.closest('tr');

            if (confirm('Are you sure you want to delete this image?')) {
                customFetch('', { // Empty URL sends the request to the current view
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({ 'delete-id': deleteId })
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            // Remove the row from the table
                            row.remove();

                            // Show success message
                            successMessageDiv.textContent = data.message;
                            successMessageDiv.classList.remove('d-none');

                            // Hide the success message after 3 seconds
                            setTimeout(() => {
                                successMessageDiv.classList.add('d-none');
                            }, 3000);
                        } else {
                            alert('Error: ' + data.message);
                        }
                    })
                    .catch(error => console.error('Error:', error));
            }
        });
    });

    // Get the current URL's query string
    const urlParams = new URLSearchParams(window.location.search);

    // Retrieve specific parameters
    const productId = urlParams.get("product_id");

    // Check and populate input fields if values are available
    if (productId) {
        document.getElementById("product-id").value = productId;
    }


    function openImageModal(imageUrl) {
        const modalImage = document.getElementById('modalImage');
        modalImage.src = imageUrl;

        // Show the modal
        const viewImageModal = new bootstrap.Modal(document.getElementById('viewImageModal'));
        viewImageModal.show();
    }
    window.openImageModal = openImageModal; // Make function accessible globally
});
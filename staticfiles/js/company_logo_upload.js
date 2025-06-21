document.addEventListener('DOMContentLoaded', function () {

    const uploadForm = document.getElementById('add-image-form');
    const successMessageDiv = document.getElementById('success-message');

    // Handle Image Upload via API
    uploadForm.addEventListener('submit', function (e) {
        e.preventDefault();

        const productId = document.getElementById('product-id').value;
        const imageInput = document.getElementById('logo-image');
        const formData = new FormData();
        formData.append('logo', imageInput.files[0]);

        customFetch(`/companies/${productId}/upload/logo`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}',
            },
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    successMessageDiv.textContent = data.message;
                    successMessageDiv.classList.remove('d-none');

                    setTimeout(() => {
                        successMessageDiv.classList.add('d-none');
                        location.reload(); // Reload page to update table with new image
                    }, 2000);
                } else {
                    alert("Error: " + data.error);
                }
            })
            .catch(error => console.error('Upload Error:', error));
    });

    // Function to Open Image Modal
    function openImageModal(imageUrl) {
        const modalImage = document.getElementById('modalImage');
        modalImage.src = imageUrl;
        const viewImageModal = new bootstrap.Modal(document.getElementById('viewImageModal'));
        viewImageModal.show();
    }

    window.openImageModal = openImageModal; // Make function accessible globally
});
document.querySelector('.btn-add-to-cart').addEventListener('click', function() {
    // Get the product details from Django template variables
    const product = {
        pno: '{{ pno }}',   
        Fileid:'{{ fileid }}',                   // Using Django template variable
        itemno: '{{ itemno }}',                  // Using same as pno if itemno not available
        name: '{{ itemname|escapejs }}',      // Escaping JavaScript special characters
        price: parseFloat('{{ buyprice }}'),  // Using buyprice from template
        image: ''                            // Default empty string (no image in your template)
    };
    
    // Get quantity
    const quantity = parseInt(document.getElementById('quantity').value) || 1;
    
    // Add to cart with quantity using the new function
    addToCartWithQuantity(
        product.pno,
        product.Fileid,
        product.itemno,
        product.name,
        product.price,
        product.image,
        quantity
    );
    
    // Animation
    const button = this;
    button.innerHTML = '<i class="fas fa-check me-2"></i> تمت الإضافة للسلة!';
    button.style.backgroundColor = '#27ae60';
    setTimeout(() => {
        button.innerHTML = '<i class="fas fa-cart-plus me-2"></i> أضف إلى السلة';
        button.style.backgroundColor = '';
    }, 2000);
});

// Function to load product image
async function loadProductImage() {
    const placeholder = document.querySelector('.product-image-placeholder');
    const pno = placeholder.dataset.productId || '{{ pno }}';

    try {
        console.log(`Fetching image for product number: ${pno}`);

        const response = await customFetch(`/hozma/api/products/${pno}/get-images`);
        console.log('Raw response from API:', response);

        // Check if the response is valid JSON and handle it
        if (response.ok) {
            const data = await response.json();

            if (Array.isArray(data) && data.length > 0) {
                let imagesHtml = data.map((img, index) => `
                    <img src="${baseUrl}${img.image_obj}" 
                         class="img-fluid product-image ${index === 0 ? 'active' : ''}" 
                         style="max-width: 100%; max-height: 400px; object-fit: contain; border-radius: 8px; display: ${index === 0 ? 'block' : 'none'};"
                         alt="Product Image ${index + 1}">
                `).join('');

                placeholder.innerHTML = `
                    <div class="image-carousel-wrapper" style="position: relative;">
                        ${imagesHtml}
                        <button class="carousel-btn prev-btn" style="position: absolute; top: 50%; left: 10px;">&#10094;</button>
                        <button class="carousel-btn next-btn" style="position: absolute; top: 50%; right: 10px;">&#10095;</button>
                    </div>
                `;

                addCarouselFunctionality(placeholder);
                placeholder.classList.remove('product-image-placeholder');
                console.log(`Product images loaded for pno: ${pno}`);
            } else {
                showPlaceholderIcon(placeholder);
                console.log(`Showing placeholder for pno: ${pno}`);
            }
        } else {
            console.error(`Error fetching product images: ${response.statusText}`);
            showPlaceholderIcon(placeholder);
        }

    } catch (error) {
        console.error('Error loading product image:', error);
        showPlaceholderIcon(placeholder);
    }
}


function showPlaceholderIcon(placeholder) {
    placeholder.innerHTML = '<i class="fas fa-car-parts fa-4x opacity-50"></i>';
    placeholder.classList.add('product-image-placeholder');
}

function addCarouselFunctionality(placeholder) {
    const images = placeholder.querySelectorAll('.product-image');
    let currentIndex = 0;

    const showImage = (index) => {
        images.forEach((img, i) => {
            img.style.display = i === index ? 'block' : 'none';
        });
    };

    placeholder.querySelector('.prev-btn').addEventListener('click', () => {
        currentIndex = (currentIndex - 1 + images.length) % images.length;
        showImage(currentIndex);
    });

    placeholder.querySelector('.next-btn').addEventListener('click', () => {
        currentIndex = (currentIndex + 1) % images.length;
        showImage(currentIndex);
    });
}

// Call when page loads
document.addEventListener('DOMContentLoaded', loadProductImage);

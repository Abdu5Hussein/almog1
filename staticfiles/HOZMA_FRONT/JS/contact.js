
const clientId = JSON.parse(localStorage.getItem("session_data@user_id"));
    // Initialize FAQ collapse items
    document.addEventListener('DOMContentLoaded', function() {
      const faqHeaders = document.querySelectorAll('.faq-header');
      
      faqHeaders.forEach(header => {
        header.addEventListener('click', function() {
          const icon = this.querySelector('i');
          if (this.getAttribute('aria-expanded') === 'true') {
            icon.classList.remove('bi-chevron-up');
            icon.classList.add('bi-chevron-down');
          } else {
            icon.classList.remove('bi-chevron-down');
            icon.classList.add('bi-chevron-up');
          }
        });
      });
    });


    document.getElementById('contactForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Disable submit button to prevent multiple submissions
    const submitBtn = e.target.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="bi bi-arrow-repeat spin"></i> جاري الإرسال...';
    
    // Get form values
    const formData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
      
        subject: document.getElementById('subject').value,
        message: document.getElementById('message').value
    };
    
    // Construct the WhatsApp message (Arabic format)
    const whatsappMessage = `
📌 *تم استقبال رسالتك* 📌

*الاسم:* ${formData.name}
*البريد الإلكتروني:* ${formData.email}

*الموضوع:* ${formData.subject}

*الرسالة:*
${formData.message}

📩 *الرجاء الانتظار ليتم الرد* 📩

عزيزنا العميل ${formData.name}،

تم استلام رسالتك بخصوص "${formData.subject}" وسيقوم فريقنا المختص بالرد عليك في أقرب وقت ممكن.

نعتز بثقتك بنا ونسعد دائما بخدمتك.

للاستفسار الفوري، يمكنك التواصل على الرقم:
+218914262604

مع خالص التقدير،
فريق مارين
    `;
    
    // Prepare data for API
    const apiData = {
        clientid: clientId, // Replace with actual client ID from session
        message: whatsappMessage
    };
    
    // Send to API
    fetch('/hozma/api/send-whatsapp-contact/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(apiData)
    })
    .then(response => {
        // First check if the response is OK (status 200-299)
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        const responseDiv = document.getElementById('responseMessage');
        
        // Check the actual API response structure
        if (data.status === "sent") {
            responseDiv.innerHTML = `
                <div class="alert alert-success">
                    <i class="bi bi-check-circle-fill"></i>
                    شكراً لك! تم إرسال رسالتك إلى واتساب. إذا كنت قد أدخلت رقمك بشكل صحيح في المعلومات، يمكنك التحقق من ذلك في ال،اتساب الخاص بك. شكرًا لتعاملك معنا!
                </div>
            `;
            document.getElementById('contactForm').reset();
        } else {
            throw new Error(data.message || 'Unknown error occurred');
        }
        
        responseDiv.style.display = 'block';
        responseDiv.scrollIntoView({ behavior: 'smooth' });
    })
    .catch(error => {
        console.error('Error:', error);
        const responseDiv = document.getElementById('responseMessage');
        responseDiv.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle-fill"></i>
                حدث خطأ أثناء إرسال الرسالة: ${error.message}
            </div>
        `;
        responseDiv.style.display = 'block';
        responseDiv.scrollIntoView({ behavior: 'smooth' });
    })
    .finally(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-send-fill"></i> إرسال الرسالة';
    });
});

// Function to get CSRF token
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

// Add spinner animation
const style = document.createElement('style');
style.innerHTML = `
    .spin {
        animation: spin 1s linear infinite;
    }
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);
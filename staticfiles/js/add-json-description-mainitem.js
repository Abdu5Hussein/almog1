// add-json-description-mainitem.js

document.addEventListener("DOMContentLoaded", function () {
    // Initialize form elements
    const form = document.getElementById("keyValueForm");
    const pnoSelect = document.getElementById("pno");
    const nameInput = document.getElementById("name");
    const companyInput = document.getElementById("company");
    const addKeyBtn = document.getElementById("addKey");
    const keyValueContainer = document.getElementById("keyValueContainer");

    // Add new key-value pair
    function addKeyValue() {
        const newPair = document.createElement("div");
        newPair.classList.add("key-value-pair", "d-flex", "align-items-center", "gap-2");

        newPair.innerHTML = `
            <input type="text" name="key" class="form-control" placeholder="المفتاح (مثال: الوزن)" required>
            <input type="text" name="value" class="form-control" placeholder="القيمة (مثال: 2 كجم)" required>
            <button type="button" class="remove-btn" title="إزالة">
                <i class="fas fa-trash-alt"></i>
            </button>
        `;

        keyValueContainer.appendChild(newPair);

        // Add event listener to the new remove button
        newPair.querySelector('.remove-btn').addEventListener('click', function () {
            removeKeyValue(this);
        });
    }

    // Remove key-value pair
    function removeKeyValue(button) {
        const pairs = keyValueContainer.querySelectorAll('.key-value-pair');
        if (pairs.length > 1) {
            button.closest('.key-value-pair').remove();
        } else {
            showAlert("يجب أن يحتوي النموذج على مواصفة واحدة على الأقل", "warning");
        }
    }

    // Update product info when selection changes
    pnoSelect.addEventListener("change", function () {
        const selectedOption = this.options[this.selectedIndex];
        nameInput.value = selectedOption.getAttribute("data-name") || "";
        companyInput.value = selectedOption.getAttribute("data-company") || "";
    });

    // Form submission handler
    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const pno = pnoSelect.value;
        if (!pno) {
            showAlert("الرجاء اختيار منتج", "warning");
            return;
        }

        // Collect key-value pairs
        const keyValuePairs = {};
        let isValid = true;
        let emptyKeyFound = false;

        document.querySelectorAll(".key-value-pair").forEach(function (pair) {
            const keyInput = pair.querySelector("input[name='key']");
            const valueInput = pair.querySelector("input[name='value']");

            const key = keyInput.value.trim();
            const value = valueInput.value.trim();

            if (!key && !emptyKeyFound) {
                keyInput.focus();
                showAlert("الرجاء إدخال مفتاح لكل مواصفة", "warning");
                isValid = false;
                emptyKeyFound = true;
                return;
            }

            if (key) {
                keyValuePairs[key] = value;
            }
        });

        if (!isValid || Object.keys(keyValuePairs).length === 0) {
            if (!emptyKeyFound) {
                showAlert("الرجاء إدخال مواصفات واحدة على الأقل", "warning");
            }
            return;
        }

        try {
            // Show loading state
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = `
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                جاري الحفظ...
            `;

            // Send data to server
            const response = await fetch(`/api/products/${pno}/add-json-description`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken(),
                },
                body: JSON.stringify({ json: keyValuePairs })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || "فشل في حفظ البيانات");
            }

            showAlert("تم حفظ المواصفات بنجاح", "success");
            console.log("Success:", data);

            // Reset form after successful submission
            resetForm();

        } catch (error) {
            console.error("Error:", error);
            showAlert(`فشل في حفظ البيانات: ${error.message}`, "danger");
        } finally {
            // Restore button state
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            }
        }
    });

    // Helper function to reset form
    function resetForm() {
        // Reset select and readonly inputs
        pnoSelect.value = "";
        nameInput.value = "";
        companyInput.value = "";

        // Remove all key-value pairs except the first one
        const pairs = keyValueContainer.querySelectorAll('.key-value-pair');
        for (let i = 1; i < pairs.length; i++) {
            pairs[i].remove();
        }

        // Clear the first pair inputs
        const firstPair = keyValueContainer.querySelector('.key-value-pair');
        if (firstPair) {
            firstPair.querySelector("input[name='key']").value = "";
            firstPair.querySelector("input[name='value']").value = "";
        }
    }

    // Helper function to show alerts
    function showAlert(message, type) {
        // Remove any existing alerts
        const existingAlert = document.querySelector('.alert');
        if (existingAlert) {
            existingAlert.remove();
        }

        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show mt-3`;
        alertDiv.setAttribute('role', 'alert');
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        // Position at top of form
        form.prepend(alertDiv);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alertDiv);
            bsAlert.close();
        }, 5000);
    }

    // CSRF Token helper function
    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    // Event listeners
    addKeyBtn.addEventListener("click", addKeyValue);

    // Event delegation for remove buttons
    keyValueContainer.addEventListener('click', function (e) {
        if (e.target.closest('.remove-btn')) {
            removeKeyValue(e.target.closest('.remove-btn'));
        }
    });
});
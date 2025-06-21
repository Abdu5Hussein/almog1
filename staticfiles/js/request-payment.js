document.addEventListener('DOMContentLoaded', function () {
    function getCSRFToken() {
        // Get the CSRF token from the cookie or from the meta tag
        let csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        return csrfToken;
    }

    function acceptLoan(clientId) {
        event.preventDefault();
        let inputField = document.getElementById('accepted-amount-' + clientId);
        let loanAmount = inputField.value;

        if (!loanAmount || loanAmount <= 0) {
            alert('Please enter a valid loan amount');
            return;
        }

        // Prepare the data to send in the POST request
        let data = {
            loan_amount: loanAmount,
            action: "accept",
        };
        console.log(data);

        // Send the POST request using Fetch API
        customFetch(`/api/payment-requests/${clientId}/accept`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                "X-CSRFToken": getCSRFToken(), // Add CSRF token
            },
            body: JSON.stringify(data)
        })
            .then(response => {
                if (!response.ok) {
                    // If the response is not OK, throw an error
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();  // Assuming the response is JSON
            })
            .then(data => {
                // Handle the successful response
                if (data && data.message) {
                    alert('Accepted loan for request ID: ' + clientId + ' with amount: ' + loanAmount);
                } else if (data && data.error) {
                    alert('Error: ' + data.error);
                } else {
                    alert('Unexpected response: ' + JSON.stringify(data));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('There was an error processing the loan request: ' + error.message);
            });
    }


    function rejectLoan(clientId) {
        // Prepare the data to send in the POST request
        event.preventDefault();
        let data = {
            action: "reject",
        };
        console.log(data);
        // Send the POST request using Fetch API
        customFetch(`/api/payment-requests/${clientId}/accept`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                "X-CSRFToken": getCSRFToken(), // Add CSRF token
            },
            body: JSON.stringify(data)
        })
            .then(response => {
                if (!response.ok) {
                    // If the response is not OK, throw an error
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // Handle the successful response
                if (data.message) {
                    alert('Rejected loan for request ID: ' + clientId);
                    // Optionally handle the response data further (e.g., update UI)
                } else {
                    alert('Unexpected response: ' + JSON.stringify(data));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('There was an error processing the loan request: ' + error.message);
            });

    }
    window.acceptLoan = acceptLoan;
    window.rejectLoan = rejectLoan;
});
document.querySelector('.learn-more-btn').addEventListener('click', function() {
    alert('Learn more about ARITHWISE!');
});

function showPopup(message) {
    if (message) {
        alert(message);  // Simple alert for the success message
    }
}

document.querySelector('.sign-in-btn').addEventListener('click', function(event) {
    event.preventDefault(); // Prevent the default form submission

    // Collect input values
    const email = document.querySelector('input[type="email"]').value;
    const password = document.querySelector('input[type="password"]').value;

    // Create the JSON data
    const data = {
        email: email,
        password: password,
    };

    // Send the JSON data to the Flask backend using fetch
    fetch('/signin', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json()) // Always parse the response as JSON
    .then(data => {
        if (data.success) {
            // If login is successful, show success message and redirect
            alert(`Message: ${data.message}`);
            window.location.href = '/dashboard'; // Redirect to dashboard
        } else {
            // If login fails, show error message
            alert(`Error: ${data.message}`);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred during sign-in');
    });
});

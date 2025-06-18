document.addEventListener('DOMContentLoaded', function() {
    const registrationButtons = document.querySelectorAll('.registration-button');
    
    registrationButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const eventId = this.dataset.eventId;
            
            fetch(`/events/${eventId}/toggle-registration/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Toggle the button's appearance
                    this.classList.toggle('active', data.is_registered);
                    // Update the icon
                    const icon = this.querySelector('i');
                    if (icon) {
                        icon.classList.toggle('fas', data.is_registered);
                        icon.classList.toggle('far', !data.is_registered);
                    }
                    // Update the text
                    const text = this.querySelector('span');
                    if (text) {
                        text.textContent = data.is_registered ? 'Отменить регистрацию' : 'Зарегистрироваться';
                    }
                    // Update participants count if element exists
                    const countElement = document.querySelector('.participants-count');
                    if (countElement) {
                        countElement.textContent = data.participants_count;
                    }
                    // Show success message
                    showMessage('success', data.message);
                } else {
                    showMessage('error', data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('error', 'Произошла ошибка при обработке запроса');
            });
        });
    });
});

// Function to get CSRF token from cookies
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

// Function to show messages
function showMessage(type, text) {
    const messageContainer = document.getElementById('message-container');
    if (!messageContainer) {
        console.error('Message container not found');
        return;
    }

    const messageElement = document.createElement('div');
    messageElement.classList.add('alert', `alert-${type === 'error' ? 'danger' : 'success'}`);
    messageElement.textContent = text;

    messageContainer.appendChild(messageElement);

    // Remove message after 3 seconds
    setTimeout(() => {
        messageElement.remove();
    }, 3000);
} 
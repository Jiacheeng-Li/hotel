// Admin Messages Management JavaScript

function markAsRead(messageId) {
    fetch(`/admin/messages/${messageId}/read`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while marking the message as read.');
    });
}

function deleteMessage(messageId) {
    if (!confirm('Are you sure you want to delete this message?')) {
        return;
    }
    
    fetch(`/admin/messages/${messageId}/delete`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while deleting the message.');
    });
}

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Mark as read button handlers
    document.querySelectorAll('.mark-read-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const messageId = parseInt(this.getAttribute('data-message-id'));
            if (messageId) {
                markAsRead(messageId);
            }
        });
    });
    
    // Delete message button handlers
    document.querySelectorAll('.delete-message-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const messageId = parseInt(this.getAttribute('data-message-id'));
            if (messageId) {
                deleteMessage(messageId);
            }
        });
    });
});


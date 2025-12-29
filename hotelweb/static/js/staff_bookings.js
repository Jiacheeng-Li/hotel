// Staff Bookings Management JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Confirm booking
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('confirm-booking-btn')) {
            const bookingId = e.target.getAttribute('data-booking-id');
            confirmBooking(bookingId);
        }
        
        if (e.target.classList.contains('cancel-booking-btn')) {
            const bookingId = e.target.getAttribute('data-booking-id');
            cancelBooking(bookingId);
        }
    });
});

function confirmBooking(bookingId) {
    if (!confirm('Are you sure you want to confirm this booking?')) {
        return;
    }
    
    fetch(`/staff/bookings/${bookingId}/confirm`, {
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
        alert('An error occurred while confirming the booking.');
    });
}

function cancelBooking(bookingId) {
    if (!confirm('Are you sure you want to cancel this booking?')) {
        return;
    }
    
    fetch(`/staff/bookings/${bookingId}/cancel`, {
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
        alert('An error occurred while cancelling the booking.');
    });
}

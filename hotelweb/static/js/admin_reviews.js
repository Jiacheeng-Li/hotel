// Admin Reviews Management - Delete Review AJAX

document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.delete-review-btn');
    
    deleteButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const reviewId = this.getAttribute('data-review-id');
            
            if (!confirm('Are you sure you want to delete this review? This action cannot be undone.')) {
                return;
            }
            
            // Disable button during request
            this.disabled = true;
            this.textContent = 'Deleting...';
            
            fetch(`/admin/reviews/${reviewId}/delete`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Remove row from table
                    const row = this.closest('tr');
                    row.style.transition = 'opacity 0.3s';
                    row.style.opacity = '0';
                    setTimeout(() => {
                        row.remove();
                    }, 300);
                } else {
                    alert(data.message || 'Failed to delete review.');
                    this.disabled = false;
                    this.textContent = 'Delete';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
                this.disabled = false;
                this.textContent = 'Delete';
            });
        });
    });
});


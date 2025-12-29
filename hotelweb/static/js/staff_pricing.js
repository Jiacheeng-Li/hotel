// Staff Pricing Management - AJAX updates

document.addEventListener('DOMContentLoaded', function() {
    const updateButtons = document.querySelectorAll('.update-pricing-btn');
    
    updateButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const roomId = this.getAttribute('data-room-id');
            const row = this.closest('tr');
            const priceInput = row.querySelector('.price-input');
            const inventoryInput = row.querySelector('.inventory-input');
            
            const price = parseFloat(priceInput.value);
            const inventory = parseInt(inventoryInput.value);
            
            // Validation
            if (isNaN(price) || price <= 0) {
                alert('Price must be greater than 0.');
                return;
            }
            
            if (isNaN(inventory) || inventory < 1) {
                alert('Inventory must be at least 1.');
                return;
            }
            
            // Disable button during request
            this.disabled = true;
            this.textContent = 'Updating...';
            
            fetch('/staff/pricing/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    room_id: roomId,
                    price: price,
                    inventory: inventory
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    const alert = document.createElement('div');
                    alert.className = 'alert alert-success alert-dismissible fade show';
                    alert.innerHTML = `
                        ${data.message}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    `;
                    document.querySelector('.container').insertBefore(alert, document.querySelector('.container').firstChild);
                    
                    // Auto-dismiss after 3 seconds
                    setTimeout(() => {
                        alert.remove();
                    }, 3000);
                } else {
                    alert(data.message || 'Failed to update pricing.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            })
            .finally(() => {
                this.disabled = false;
                this.textContent = 'Update';
            });
        });
    });
});


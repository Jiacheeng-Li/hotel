// Admin Users Management JavaScript - Hotel Search and Grant Points

document.addEventListener('DOMContentLoaded', function() {
    // Hotel search functionality
    const searchInput = document.getElementById('hotel-search');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase().trim();
            const hotelItems = document.querySelectorAll('.hotel-item');
            
            hotelItems.forEach(item => {
                const name = item.getAttribute('data-hotel-name') || '';
                const city = item.getAttribute('data-hotel-city') || '';
                const address = item.getAttribute('data-hotel-address') || '';
                
                if (searchTerm === '' || name.includes(searchTerm) || city.includes(searchTerm) || address.includes(searchTerm)) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }
    
    // Grant points functionality
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('grant-points-btn') || e.target.closest('.grant-points-btn')) {
            const btn = e.target.classList.contains('grant-points-btn') ? e.target : e.target.closest('.grant-points-btn');
            const userId = btn.getAttribute('data-user-id');
            const username = btn.getAttribute('data-username');
            
            const points = prompt(`Enter points to grant to ${username}:`);
            if (points === null) return; // User cancelled
            
            const pointsNum = parseInt(points);
            if (isNaN(pointsNum) || pointsNum <= 0) {
                alert('Please enter a valid positive number.');
                return;
            }
            
            const description = prompt('Enter description (optional):') || 'Admin grant';
            
            fetch(`/admin/users/${userId}/grant-points`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    points: pointsNum,
                    description: description
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    location.reload();
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while granting points.');
            });
        }
    });
});

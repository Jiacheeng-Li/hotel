// Admin Edit Hotel - Room Management JavaScript

function loadRoomData(roomId, name, capacity, price, inventory, description, imageUrl, amenityIds) {
    document.getElementById('room_name_' + roomId).value = name;
    document.getElementById('capacity_' + roomId).value = capacity;
    document.getElementById('price_per_night_' + roomId).value = price;
    document.getElementById('inventory_' + roomId).value = inventory;
    document.getElementById('room_description_' + roomId).value = description || '';
    document.getElementById('room_image_url_' + roomId).value = imageUrl || '';
    
    // Clear all checkboxes first
    const checkboxes = document.querySelectorAll('#editRoom_' + roomId + ' input[type="checkbox"]');
    checkboxes.forEach(cb => cb.checked = false);
    
    // Check the amenities that this room has
    amenityIds.forEach(amenityId => {
        const checkbox = document.getElementById('amenity_' + roomId + '_' + amenityId);
        if (checkbox) {
            checkbox.checked = true;
        }
    });
}

function deleteRoom(roomId, roomName) {
    if (!confirm(`Are you sure you want to delete the room type "${roomName}"? This action cannot be undone.`)) {
        return;
    }
    
    // Create a form to submit the delete request
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = window.location.href;
    
    // Add CSRF token - try to find it from any form on the page
    const csrfInputs = document.querySelectorAll('input[name="csrf_token"]');
    if (csrfInputs.length === 0) {
        alert('Error: CSRF token not found. Please refresh the page and try again.');
        return;
    }
    const csrfToken = csrfInputs[0].value;
    
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrf_token';
    csrfInput.value = csrfToken;
    form.appendChild(csrfInput);
    
    // Add action
    const actionInput = document.createElement('input');
    actionInput.type = 'hidden';
    actionInput.name = 'action';
    actionInput.value = 'delete_room';
    form.appendChild(actionInput);
    
    // Add room_id
    const roomIdInput = document.createElement('input');
    roomIdInput.type = 'hidden';
    roomIdInput.name = 'room_id';
    roomIdInput.value = roomId;
    form.appendChild(roomIdInput);
    
    // Submit form
    document.body.appendChild(form);
    form.submit();
}

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Delete room button handlers
    document.querySelectorAll('.delete-room-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const roomId = this.getAttribute('data-room-id');
            const roomName = this.getAttribute('data-room-name');
            if (roomId && roomName) {
                deleteRoom(parseInt(roomId), roomName);
            }
        });
    });
    
    // Edit room button handlers - load room data when edit button is clicked
    document.querySelectorAll('.edit-room-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const roomId = parseInt(this.getAttribute('data-room-id'));
            const name = this.getAttribute('data-room-name');
            const capacity = parseInt(this.getAttribute('data-room-capacity'));
            const price = parseFloat(this.getAttribute('data-room-price'));
            const inventory = parseInt(this.getAttribute('data-room-inventory'));
            const description = this.getAttribute('data-room-description') || '';
            const imageUrl = this.getAttribute('data-room-image') || '';
            const amenitiesJson = this.getAttribute('data-room-amenities');
            let amenityIds = [];
            try {
                amenityIds = JSON.parse(amenitiesJson);
            } catch (e) {
                console.error('Error parsing amenities:', e);
            }
            
            loadRoomData(roomId, name, capacity, price, inventory, description, imageUrl, amenityIds);
        });
    });
});


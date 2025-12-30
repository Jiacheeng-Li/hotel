// Favorites functionality
function toggleFavorite(hotelId, event) {
    if (!hotelId) return;
    
    // Support both .btn-favorite (hotel detail page) and .hotel-card-favorite (hotel cards)
    const button = (event && (event.target.closest('.btn-favorite') || event.target.closest('.hotel-card-favorite'))) || 
                   document.querySelector(`[data-hotel-id="${hotelId}"]`);
    if (!button) return;
    
    const icon = button.querySelector('i');
    const isCurrentlyFavorited = button.classList.contains('favorited');
    
    // Find the hotel card container (for removal from favorites page)
    const hotelCard = button.closest('.card.mb-4') || button.closest('.hotel-card') || button.closest('.card');
    
    // Optimistic UI update
    if (isCurrentlyFavorited) {
        button.classList.remove('favorited');
        icon.classList.remove('bi-heart-fill');
        icon.classList.add('bi-heart');
    } else {
        button.classList.add('favorited');
        icon.classList.remove('bi-heart');
        icon.classList.add('bi-heart-fill');
    }
    
    // Send AJAX request
    fetch(`/favorite/hotel/${hotelId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update all favorite buttons for this hotel on the page
            document.querySelectorAll(`[data-hotel-id="${hotelId}"]`).forEach(btn => {
                const btnIcon = btn.querySelector('i');
                if (data.is_favorited) {
                    btn.classList.add('favorited');
                    btnIcon.classList.remove('bi-heart');
                    btnIcon.classList.add('bi-heart-fill');
                    btn.setAttribute('aria-label', 'Remove from favorites');
                } else {
                    btn.classList.remove('favorited');
                    btnIcon.classList.remove('bi-heart-fill');
                    btnIcon.classList.add('bi-heart');
                    btn.setAttribute('aria-label', 'Add to favorites');
                }
            });
            
            // If unfavorited and we're on the favorites tab, remove the hotel card
            if (!data.is_favorited) {
                // Find the hotel card in favorites tab using data attribute
                const favoritesTab = document.getElementById('favorites');
                if (favoritesTab) {
                    const hotelCardToRemove = favoritesTab.querySelector(`[data-hotel-card-id="${hotelId}"]`);
                    if (hotelCardToRemove) {
                        // Remove the hotel card with animation
                        hotelCardToRemove.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                        hotelCardToRemove.style.opacity = '0';
                        hotelCardToRemove.style.transform = 'translateX(-20px)';
                        
                        setTimeout(() => {
                            hotelCardToRemove.remove();
                            
                            // Check if favorites tab is now empty
                            const remainingCards = favoritesTab.querySelectorAll('.favorite-hotel-card');
                            if (remainingCards.length === 0) {
                                // Show empty state
                                const emptyState = favoritesTab.querySelector('.empty-state');
                                if (!emptyState) {
                                const emptyStateHTML = `
                                    <div class="empty-state">
                                        <div class="empty-state-icon"><i class="bi bi-heart" aria-hidden="true"></i></div>
                                        <h3>No Favorite Hotels</h3>
                                        <p>You haven't added any hotels to your favorites yet</p>
                                        <p class="text-muted small">Click the heart icon on any hotel to add it to your favorites</p>
                                        <a href="/" class="btn-primary">Explore Hotels</a>
                                    </div>
                                `;
                                    favoritesTab.insertAdjacentHTML('beforeend', emptyStateHTML);
                                } else {
                                    emptyState.style.display = 'block';
                                }
                            }
                            
                            // Update favorites badge count
                            const favoritesTabButton = document.querySelector('[data-tab="favorites"]');
                            if (favoritesTabButton) {
                                const badge = favoritesTabButton.querySelector('.badge');
                                if (badge) {
                                    const currentCount = parseInt(badge.textContent.trim()) || 0;
                                    const newCount = Math.max(0, currentCount - 1);
                                    badge.textContent = newCount;
                                    if (newCount === 0) {
                                        badge.style.display = 'none';
                                    }
                                }
                            }
                        }, 300);
                    }
                }
            }
        } else {
            // Revert optimistic update on error
            if (isCurrentlyFavorited) {
                button.classList.add('favorited');
                icon.classList.remove('bi-heart');
                icon.classList.add('bi-heart-fill');
            } else {
                button.classList.remove('favorited');
                icon.classList.remove('bi-heart-fill');
                icon.classList.add('bi-heart');
            }
        }
    })
    .catch(error => {
        console.error('Error toggling favorite:', error);
        // Revert optimistic update on error
        if (isCurrentlyFavorited) {
            button.classList.add('favorited');
            icon.classList.remove('bi-heart');
            icon.classList.add('bi-heart-fill');
        } else {
            button.classList.remove('favorited');
            icon.classList.remove('bi-heart-fill');
            icon.classList.add('bi-heart');
        }
    });
}

// Initialize favorite buttons on page load
document.addEventListener('DOMContentLoaded', function() {
    // Use event delegation for better performance and dynamic content support
    document.addEventListener('click', function(e) {
        // Check if clicked element or its parent is a favorite button
        const button = e.target.closest('.btn-favorite, .hotel-card-favorite');
        if (button) {
            e.preventDefault();
            e.stopPropagation();
            const hotelId = button.getAttribute('data-hotel-id');
            if (hotelId) {
                toggleFavorite(parseInt(hotelId), e);
            }
        }
    });
});


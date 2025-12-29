// Celebration Modal JavaScript

function closeCelebrationModal() {
    const modal = document.getElementById('celebrationModal');
    if (modal) {
        modal.classList.remove('show');
        // Use fetch to tell server to clear the session variable
        const clearUrl = modal.getAttribute('data-clear-url');
        if (clearUrl) {
            fetch(clearUrl, {method: 'POST'});
        }
    }
}

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    const closeBtn = document.getElementById('celebration-close-btn');
    const celebrationBtn = document.getElementById('celebration-btn');
    
    if (closeBtn) {
        closeBtn.addEventListener('click', closeCelebrationModal);
    }
    
    if (celebrationBtn) {
        celebrationBtn.addEventListener('click', closeCelebrationModal);
    }
});


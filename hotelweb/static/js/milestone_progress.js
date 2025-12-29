// Milestone Progress Logic
function toggleRules() {
    const content = document.getElementById('rules-content');
    const icon = document.getElementById('rules-toggle-icon');
    
    if (content.classList.contains('expanded')) {
        content.classList.remove('expanded');
        icon.classList.remove('expanded');
    } else {
        content.classList.add('expanded');
        icon.classList.add('expanded');
    }
}

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    const rulesHeader = document.getElementById('rules-header');
    if (rulesHeader) {
        rulesHeader.addEventListener('click', toggleRules);
    }
});


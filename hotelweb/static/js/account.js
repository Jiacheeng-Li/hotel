// Account Page Functions
function switchTab(tabName, event) {
    if (event) {
        event.preventDefault();
    }
    
    // Hide all tabs
    const tabs = document.querySelectorAll('.account-page-wrapper .tab-content');
    if (tabs.length === 0) {
        // Fallback for when wrapper might not be present or different structure
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
            tab.style.display = 'none'; // Explicitly hide
        });
    } else {
        tabs.forEach(tab => {
            tab.classList.remove('active');
        });
    }
    
    // Remove active class from all nav tabs
    document.querySelectorAll('.nav-tab').forEach(nav => {
        nav.classList.remove('active');
    });
    
    // Show selected tab
    const targetTab = document.getElementById(tabName);
    if (targetTab) {
        targetTab.classList.add('active');
        targetTab.style.display = ''; // Reset inline display if set
    } else {
        console.error(`Tab content with ID '${tabName}' not found`);
    }
    
    // Add active class to clicked nav tab
    if (event && event.currentTarget) {
        event.currentTarget.classList.add('active');
    } else {
        // Fallback: Find the nav tab that matches the tabName via data-tab or onclick
        const navTab = document.querySelector(`.nav-tab[data-tab="${tabName}"]`);
        if (navTab) {
            navTab.classList.add('active');
        } else {
            document.querySelectorAll('.nav-tab').forEach(nav => {
                if (nav.getAttribute('onclick') && nav.getAttribute('onclick').includes(tabName)) {
                    nav.classList.add('active');
                }
            });
        }
    }
    
    return false;
}

function switchTracker(type) {
    const nightsTracker = document.getElementById('nights-tracker');
    const pointsTracker = document.getElementById('points-tracker');
    const toggleBtns = document.querySelectorAll('.toggle-btn');
    
    toggleBtns.forEach(btn => btn.classList.remove('active'));
    
    if (type === 'nights') {
        if (nightsTracker) nightsTracker.style.display = 'block';
        if (pointsTracker) pointsTracker.style.display = 'none';
        if (toggleBtns[0]) toggleBtns[0].classList.add('active');
    } else {
        if (nightsTracker) nightsTracker.style.display = 'none';
        if (pointsTracker) pointsTracker.style.display = 'block';
        if (toggleBtns[1]) toggleBtns[1].classList.add('active');
    }
}

function toggleBenefitsComparison(e) {
    if (e) {
        e.preventDefault();
    }
    const comparison = document.getElementById('benefits-comparison');
    const icon = document.getElementById('benefits-icon');
    if (comparison) {
        comparison.classList.toggle('show');
        if (icon) {
            if (comparison.classList.contains('show')) {
                icon.className = 'bi bi-chevron-up';
            } else {
                icon.className = 'bi bi-chevron-down';
            }
        }
    }
    return false;
}

function toggleRetentionRules() {
    const modal = document.getElementById('retention-rules-modal');
    if (modal) {
        modal.style.display = modal.style.display === 'none' ? 'flex' : 'none';
    }
}

// Close modal when clicking on backdrop
window.onclick = function(event) {
    const modal = document.getElementById('retention-rules-modal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}

function toggleEdit() {
    const viewElements = document.querySelectorAll('[id^="view-"]');
    const editElements = document.querySelectorAll('[id^="edit-"]');
    const formActions = document.getElementById('formActions');

    viewElements.forEach(el => el.style.display = 'none');
    editElements.forEach(el => el.style.display = 'block');
    if (formActions) formActions.style.display = 'flex';
}

function cancelEdit() {
    const viewElements = document.querySelectorAll('[id^="view-"]');
    const editElements = document.querySelectorAll('[id^="edit-"]');
    const formActions = document.getElementById('formActions');

    viewElements.forEach(el => el.style.display = 'block');
    editElements.forEach(el => el.style.display = 'none');
    if (formActions) formActions.style.display = 'none';
}

// My Stays Tab functionality (if present on page)
document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-button');
    if (tabButtons.length > 0) {
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const tabName = button.dataset.tab;

                // Update active button
                document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');

                // Update active content
                document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
                const targetContent = document.getElementById(tabName);
                if (targetContent) {
                    targetContent.classList.add('active');
                }
            });
        });
    }
    
    // Auto-select tab if URL hash exists
    const hash = window.location.hash.substring(1);
    if (hash) {
        const tabLink = document.querySelector(`.nav-tab[data-tab="${hash}"]`);
        if (tabLink) {
            switchTab(hash);
        }
    }
});

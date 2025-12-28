// Account Page Functions
function switchTab(tabName, event) {
    console.log('Switching to tab:', tabName);
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
    // Hide all trackers
    document.querySelectorAll('.tracker-content').forEach(el => el.style.display = 'none');
    
    // Deactivate all toggles
    document.querySelectorAll('.toggle-btn').forEach(el => el.classList.remove('active'));
    
    // Show selected tracker
    document.getElementById(type + '-tracker').style.display = 'block';
    document.getElementById(type + '-toggle').classList.add('active');
}

function toggleBenefitsComparison(event) {
    if (event) event.preventDefault();
    const comparison = document.getElementById('benefits-comparison');
    const icon = document.getElementById('benefits-icon');
    
    if (comparison.classList.contains('show')) {
        comparison.classList.remove('show');
        icon.classList.remove('bi-chevron-up');
        icon.classList.add('bi-chevron-down');
    } else {
        comparison.classList.add('show');
        icon.classList.remove('bi-chevron-down');
        icon.classList.add('bi-chevron-up');
    }
    return false;
}

function toggleRetentionRules() {
    const modal = document.getElementById('retention-rules-modal');
    if (modal) {
        modal.style.display = (modal.style.display === 'flex' ? 'none' : 'flex');
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('retention-rules-modal');
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

function toggleEdit() {
    // Enable inputs
    document.querySelectorAll('.profile-input').forEach(input => {
        input.style.display = 'block';
    });
    
    // Hide static text
    document.getElementById('view-username').style.display = 'none';
    document.getElementById('view-email').style.display = 'none';
    document.getElementById('view-phone').style.display = 'none';
    document.getElementById('view-birthday').style.display = 'none';
    document.getElementById('view-address').style.display = 'none';
    document.getElementById('view-city').style.display = 'none';
    document.getElementById('view-country').style.display = 'none';
    document.getElementById('view-postal').style.display = 'none';
    
    // Show buttons
    document.getElementById('formActions').style.display = 'flex';
    
    // Hide edit button
    document.querySelector('.btn-edit').style.display = 'none';
}

function cancelEdit() {
    // Hide inputs
    document.querySelectorAll('.profile-input').forEach(input => {
        input.style.display = 'none';
    });
    
    // Show static text
    document.getElementById('view-username').style.display = 'inline';
    document.getElementById('view-email').style.display = 'inline';
    document.getElementById('view-phone').style.display = 'inline';
    document.getElementById('view-birthday').style.display = 'inline';
    document.getElementById('view-address').style.display = 'inline';
    document.getElementById('view-city').style.display = 'inline';
    document.getElementById('view-country').style.display = 'inline';
    document.getElementById('view-postal').style.display = 'inline';
    
    // Hide buttons
    document.getElementById('formActions').style.display = 'none';
    
    // Show edit button
    document.querySelector('.btn-edit').style.display = 'block';
}

function toggleAddCard() {
    const form = document.getElementById('add-card-form');
    const btn = document.getElementById('add-card-btn');
    if (form.style.display === 'none') {
        form.style.display = 'block';
        btn.style.display = 'none';
    } else {
        form.style.display = 'none';
        btn.style.display = 'block';
    }
}

function cancelAddCard() {
    document.getElementById('add-card-form').style.display = 'none';
    document.getElementById('add-card-btn').style.display = 'block';
}

document.addEventListener('DOMContentLoaded', function() {
    // Check URL parameters for tab selection
    const urlParams = new URLSearchParams(window.location.search);
    const tab = urlParams.get('tab');
    if (tab) {
        switchTab(tab);
    }
    
    // Setup tab click listeners if not using inline onclick
    const navTabs = document.querySelectorAll('.nav-tab');
    if (navTabs.length > 0) {
        navTabs.forEach(tab => {
            tab.addEventListener('click', function(e) {
                // If using data-tab attribute
                const tabName = this.getAttribute('data-tab');
                if (tabName) {
                    // switchTab is called via onclick in HTML, so we don't need to duplicate here
                    // unless we remove onclick from HTML
                }
            });
        });
    }
    
    // Auto-select tab if URL hash exists
    const hash = window.location.hash.substring(1);
    if (hash) {
        switchTab(hash);
    }
});

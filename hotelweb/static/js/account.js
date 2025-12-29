// Collapsible List Functions
function toggleCollapseList(button) {
    const listId = button.getAttribute('data-list-id');
    const list = button.closest('.card').querySelector('.collapsible-list');
    if (!list) return;
    
    const items = list.querySelectorAll('.collapsible-item');
    const showMoreText = button.querySelector('.show-more-text');
    const showLessText = button.querySelector('.show-less-text');
    const defaultShow = parseInt(list.getAttribute('data-default-show')) || 5;
    
    // Check if currently showing all items
    const isExpanded = Array.from(items).every((item, index) => {
        return index < defaultShow || item.style.display !== 'none';
    });
    
    if (isExpanded) {
        // Collapse: hide items beyond defaultShow
        items.forEach((item, index) => {
            if (index >= defaultShow) {
                item.style.display = 'none';
            }
        });
        showMoreText.style.display = 'inline';
        showLessText.style.display = 'none';
    } else {
        // Expand: show all items
        items.forEach((item) => {
            item.style.display = '';
        });
        showMoreText.style.display = 'none';
        showLessText.style.display = 'inline';
    }
}

// Account Page Functions
function switchTab(tabName, event) {
    console.log('Switching to tab:', tabName);
    if (event) {
        event.preventDefault();
    }
    
    // Update URL hash to maintain tab state on refresh (without scrolling)
    if (tabName && tabName !== 'overview') {
        // Use history API to update hash without scrolling
        if (history.replaceState) {
            history.replaceState(null, null, '#' + tabName);
        } else {
            // Fallback for older browsers
            const scrollY = window.scrollY;
            window.location.hash = tabName;
            window.scrollTo(0, scrollY);
        }
    } else {
        // Remove hash for overview (default tab)
        if (history.replaceState) {
            history.replaceState(null, null, window.location.pathname + window.location.search);
        } else {
            window.location.hash = '';
        }
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

// Update profile via AJAX
function updateProfile() {
    const form = document.getElementById('profileForm');
    if (!form) return;
    
    const formData = new FormData(form);
    
    // Disable submit button
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn ? submitBtn.textContent : 'Save Changes';
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Saving...';
    }
    
    fetch(form.action, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showFlashMessage(data.message, 'success');
            
            // Update view values with new data
            if (data.user) {
                updateProfileView(data.user);
            }
            
            // Exit edit mode
            cancelEdit();
        } else {
            showFlashMessage(data.message || 'Failed to update profile.', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showFlashMessage('An error occurred while updating your profile. Please try again.', 'danger');
    })
    .finally(() => {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });
}

// Update profile view values
function updateProfileView(userData) {
    const formatDate = (dateStr) => {
        if (!dateStr) return 'Not provided';
        const date = new Date(dateStr);
        const months = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December'];
        return `${months[date.getMonth()]} ${date.getDate()}, ${date.getFullYear()}`;
    };
    
    const formatValue = (value) => value || 'Not provided';
    
    document.getElementById('view-username').textContent = userData.username || 'Not provided';
    document.getElementById('view-email').textContent = userData.email || 'Not provided';
    document.getElementById('view-phone').textContent = formatValue(userData.phone);
    document.getElementById('view-birthday').textContent = formatDate(userData.birthday);
    document.getElementById('view-address').textContent = formatValue(userData.address);
    document.getElementById('view-city').textContent = formatValue(userData.city);
    document.getElementById('view-country').textContent = formatValue(userData.country);
    document.getElementById('view-postal').textContent = formatValue(userData.postal_code);
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
    // Reset form
    const form = document.getElementById('addCardForm');
    if (form) {
        form.reset();
    }
}

// Add card via AJAX
function addCard(event) {
    const form = document.getElementById('addCardForm');
    if (!form) return;
    
    // Prevent default form submission if event is provided
    if (event) {
        event.preventDefault();
    }
    
    const formData = new FormData(form);
    
    // Disable submit button
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn ? submitBtn.textContent : 'Save Card';
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Saving...';
    }
    
    fetch(form.action, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showFlashMessage(data.message, 'success');
            
            // Hide form and show button
            cancelAddCard();
            
            // Reload payment methods section or add new card to list
            location.reload(); // Simple reload for now, could be optimized to update DOM
        } else {
            showFlashMessage(data.message || 'Failed to add payment method.', 'danger');
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showFlashMessage('An error occurred while adding your payment method. Please try again.', 'danger');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });
}

// Show flash message (for AJAX operations)
function showFlashMessage(message, type = 'success') {
    const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show shadow-sm border-0 auto-dismiss" role="alert" data-auto-dismiss="3000">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    // Find the flash messages container (below navbar)
    let alertContainer = document.getElementById('flash-messages-container');
    if (!alertContainer) {
        // Create container if it doesn't exist
        alertContainer = document.createElement('div');
        alertContainer.id = 'flash-messages-container';
        alertContainer.className = 'flash-messages-container';
        const containerDiv = document.createElement('div');
        containerDiv.className = 'container';
        alertContainer.appendChild(containerDiv);
        // Insert at the beginning of body (fixed position doesn't need to be after navbar)
        document.body.insertBefore(alertContainer, document.body.firstChild);
        
        // Update position based on navbar height
        updateFlashMessagesPosition();
    }
    
    // Find or create the inner container
    let innerContainer = alertContainer.querySelector('.container');
    if (!innerContainer) {
        innerContainer = document.createElement('div');
        innerContainer.className = 'container';
        alertContainer.appendChild(innerContainer);
    }
    
    innerContainer.insertAdjacentHTML('beforeend', alertHtml);
    
    // Update position in case navbar height changed
    updateFlashMessagesPosition();
    
    // Auto-dismiss after 3 seconds
    setTimeout(() => {
        const alert = alertContainer.querySelector('.auto-dismiss:last-child');
        if (alert) {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }
    }, 3000);
}

// Update flash messages container position based on navbar height
function updateFlashMessagesPosition() {
    const navbar = document.querySelector('nav.navbar');
    const flashContainer = document.getElementById('flash-messages-container');
    if (navbar && flashContainer) {
        const navbarHeight = navbar.offsetHeight;
        flashContainer.style.top = navbarHeight + 'px';
    }
}

// Set default card via AJAX
function setDefaultCard(cardId, csrfToken) {
    const formData = new FormData();
    formData.append('csrf_token', csrfToken);
    
    // Find button before disabling
    const btn = document.querySelector(`.set-default-btn[data-card-id="${cardId}"]`);
    const originalText = btn ? btn.textContent : 'Set Default';
    const btnParent = btn ? btn.parentNode : null;
    
    if (btn) {
        btn.disabled = true;
        btn.textContent = 'Updating...';
    }
    
    fetch(`/account/payment-method/default/${cardId}`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRF-Token': csrfToken
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showFlashMessage(data.message, 'success');
            
            // Update UI: Remove "Default" badge from all cards and convert to buttons
            document.querySelectorAll('.default-badge').forEach(badge => {
                const oldCardId = badge.getAttribute('data-card-id');
                const tokenFromBadge = badge.getAttribute('data-csrf-token');
                const tokenToUse = tokenFromBadge || csrfToken;
                
                // Create new button element
                const newButton = document.createElement('button');
                newButton.type = 'button';
                newButton.className = 'btn btn-sm btn-link text-decoration-none p-0 set-default-btn';
                newButton.setAttribute('data-card-id', oldCardId);
                newButton.setAttribute('data-csrf-token', tokenToUse);
                newButton.style.color = '#1e3a8a';
                newButton.style.fontWeight = '500';
                newButton.setAttribute('aria-label', 'Set card as default');
                newButton.textContent = 'Set Default';
                
                badge.parentNode.replaceChild(newButton, badge);
            });
            
            // Add "Default" badge to the selected card (use parent to find the correct element)
            if (btnParent) {
                // Find the button in the parent (might have been replaced, so find by data attribute)
                const currentBtn = btnParent.querySelector(`.set-default-btn[data-card-id="${cardId}"]`);
                if (currentBtn) {
                    const newBadge = document.createElement('span');
                    newBadge.className = 'badge default-badge';
                    newBadge.setAttribute('data-card-id', cardId);
                    newBadge.setAttribute('data-csrf-token', csrfToken);
                    newBadge.style.backgroundColor = '#1e3a8a';
                    newBadge.style.color = 'white';
                    newBadge.style.padding = '0.375rem 0.75rem';
                    newBadge.style.fontSize = '0.75rem';
                    newBadge.style.fontWeight = '600';
                    newBadge.textContent = 'Default';
                    
                    currentBtn.parentNode.replaceChild(newBadge, currentBtn);
                }
            }
            
            // Re-attach event listeners to all "Set Default" buttons (use event delegation instead)
            // Actually, we should use event delegation from the start to avoid this issue
        } else {
            showFlashMessage(data.message || 'Failed to set default card.', 'danger');
            if (btn) {
                btn.disabled = false;
                btn.textContent = originalText;
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showFlashMessage('An error occurred. Please try again.', 'danger');
        if (btn) {
            btn.disabled = false;
            btn.textContent = originalText;
        }
    });
}

// Delete card via AJAX
function deleteCard(cardId, csrfToken, cardType, cardLast4) {
    if (!confirm(`Are you sure you want to delete your ${cardType} card ending in ${cardLast4}?`)) {
        return;
    }
    
    const formData = new FormData();
    formData.append('csrf_token', csrfToken);
    
    fetch(`/account/payment-method/delete/${cardId}`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRF-Token': csrfToken
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showFlashMessage(data.message, 'success');
            // Remove the card element from DOM
            const cardElement = document.querySelector(`[data-card-id="${cardId}"]`)?.closest('.profile-field');
            if (cardElement) {
                cardElement.style.transition = 'opacity 0.3s';
                cardElement.style.opacity = '0';
                setTimeout(() => {
                    cardElement.remove();
                    // Check if no cards left
                    const cardsList = document.querySelector('.payment-methods-list');
                    if (cardsList && cardsList.children.length === 0) {
                        cardsList.innerHTML = '<p class="text-muted text-center py-3">No payment methods saved.</p>';
                    }
                }, 300);
            } else {
                // Fallback: reload page
                location.reload();
            }
        } else {
            showFlashMessage(data.message || 'Failed to delete card.', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showFlashMessage('An error occurred. Please try again.', 'danger');
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Check URL hash first (highest priority for tab selection)
    const hash = window.location.hash.substring(1);
    if (hash && ['overview', 'rewards', 'activity', 'settings', 'benefits'].includes(hash)) {
        switchTab(hash);
        return; // Exit early if hash is found
    }
    
    // Check URL parameters for tab selection (fallback)
    const urlParams = new URLSearchParams(window.location.search);
    const tab = urlParams.get('tab');
    if (tab) {
        switchTab(tab);
        return;
    }
    
    // Default to overview if no hash or tab parameter
    // Overview tab should be active by default (handled by HTML)
    
    // Tab click listeners are handled via onclick in HTML
    // Tracker toggle buttons are handled via onclick in HTML
    // Retention rules toggle is handled via onclick in HTML
    
    // Setup AJAX handlers for payment methods
    // Use event delegation for "Set Default" buttons to handle dynamically created elements
    const paymentMethodsList = document.querySelector('.payment-methods-list');
    if (paymentMethodsList) {
        paymentMethodsList.addEventListener('click', function(e) {
            const btn = e.target.closest('.set-default-btn');
            if (btn && !btn.disabled) {
                const cardId = btn.getAttribute('data-card-id');
                const csrfToken = btn.getAttribute('data-csrf-token');
                if (cardId && csrfToken) {
                    e.preventDefault();
                    e.stopPropagation();
                    setDefaultCard(cardId, csrfToken);
                }
            }
        });
    }
    
    // Delete card buttons
    document.querySelectorAll('.delete-card-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const cardId = this.getAttribute('data-card-id');
            const csrfToken = this.getAttribute('data-csrf-token');
            const cardType = this.getAttribute('data-card-type');
            const cardLast4 = this.getAttribute('data-card-last4');
            deleteCard(cardId, csrfToken, cardType, cardLast4);
        });
    });
    
    // Add card form submission
    const addCardForm = document.getElementById('addCardForm');
    if (addCardForm) {
        addCardForm.addEventListener('submit', function(e) {
            e.preventDefault();
            addCard(e);
        });
    }
});

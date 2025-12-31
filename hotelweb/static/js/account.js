// Collapsible List Functions
function toggleCollapseList(button) {
    if (!button) return;
    
    const list = button.closest('.card').querySelector('.collapsible-list');
    if (!list) {
        console.warn('toggleCollapseList: collapsible-list not found');
        return;
    }
    
    const items = list.querySelectorAll('.collapsible-item');
    if (items.length === 0) {
        console.warn('toggleCollapseList: no collapsible-item found');
        return;
    }
    
    const showMoreText = button.querySelector('.show-more-text');
    const showLessText = button.querySelector('.show-less-text');
    const defaultShow = parseInt(list.getAttribute('data-default-show')) || 5;
    
    // Helper function to check if item is visible
    function isItemVisible(item) {
        // Check computed style - if hidden class is present, computed display will be 'none'
        const style = window.getComputedStyle(item);
        return style.display !== 'none';
    }
    
    // Check if currently showing all items (expanded state)
    // Count how many items are visible
    let visibleCount = 0;
    items.forEach((item) => {
        if (isItemVisible(item)) {
            visibleCount++;
        }
    });
    
    // If all items are visible, we're expanded; otherwise collapsed
    const isExpanded = visibleCount === items.length;
    
    if (isExpanded) {
        // Collapse: hide items beyond defaultShow
        items.forEach((item, index) => {
            if (index >= defaultShow) {
                item.style.display = 'none';
                item.classList.add('hidden');
            }
        });
        if (showMoreText) {
        showMoreText.style.display = 'inline';
            showMoreText.classList.remove('hidden');
        }
        if (showLessText) {
        showLessText.style.display = 'none';
            showLessText.classList.add('hidden');
        }
    } else {
        // Expand: show all items
        items.forEach((item) => {
            item.style.display = '';
            item.classList.remove('hidden');
        });
        if (showMoreText) {
        showMoreText.style.display = 'none';
            showMoreText.classList.add('hidden');
        }
        if (showLessText) {
        showLessText.style.display = 'inline';
            showLessText.classList.remove('hidden');
        }
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
    document.querySelectorAll('.tracker-content').forEach(el => {
        el.classList.add('hidden');
        el.style.display = 'none';
    });
    
    // Deactivate all toggles
    document.querySelectorAll('.toggle-btn').forEach(el => el.classList.remove('active'));
    
    // Show selected tracker
    const selectedTracker = document.getElementById(type + '-tracker');
    if (selectedTracker) {
        selectedTracker.classList.remove('hidden');
        selectedTracker.style.display = 'block';
    }
    const selectedToggle = document.getElementById(type + '-toggle');
    if (selectedToggle) {
        selectedToggle.classList.add('active');
    }
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
        if (modal.classList.contains('show') || modal.style.display === 'flex') {
            modal.classList.remove('show');
            modal.style.display = 'none';
        } else {
            modal.classList.add('show');
            modal.style.display = 'flex';
        }
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

// Update password via AJAX
function updatePassword() {
    const form = document.getElementById('passwordForm');
    if (!form) return;
    
    const formData = new FormData(form);
    
    // Validate that new password and confirm password match
    const newPassword = formData.get('new_password');
    const confirmPassword = formData.get('confirm_password');
    
    if (newPassword !== confirmPassword) {
        showFlashMessage('New password and confirmation do not match.', 'danger');
        return;
    }
    
    // Disable submit button
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn ? submitBtn.textContent : 'Change Password';
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Changing...';
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
            // Reset form and exit edit mode
            cancelPasswordEdit();
        } else {
            showFlashMessage(data.message || 'Failed to change password.', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showFlashMessage('An error occurred while changing your password. Please try again.', 'danger');
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
    // If add card form is open, close it first
    const addCardForm = document.getElementById('add-card-form');
    const addCardBtn = document.getElementById('add-card-btn');
    if (addCardForm && !addCardForm.classList.contains('hidden') && addCardForm.style.display !== 'none') {
        cancelAddCard();
    }
    
    // If password edit is open, close it first
    const passwordFields = document.getElementById('passwordFields');
    if (passwordFields && !passwordFields.classList.contains('hidden')) {
        cancelPasswordEdit();
    }
    
    // Enable inputs in profile form only - remove hidden class and show
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.querySelectorAll('.profile-input').forEach(input => {
        input.classList.remove('hidden');
        input.style.display = 'block';
    });
    }
    
    // Hide static text
    const viewElements = ['view-username', 'view-email', 'view-phone', 'view-birthday', 
                         'view-address', 'view-city', 'view-country', 'view-postal'];
    viewElements.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.style.display = 'none';
        }
    });
    
    // Show buttons
    const formActions = document.getElementById('formActions');
    if (formActions) {
        formActions.classList.remove('hidden');
        formActions.style.display = 'flex';
    }
    
    // Hide edit profile button specifically
    const editProfileBtn = document.getElementById('edit-profile-btn');
    if (editProfileBtn) {
        editProfileBtn.style.display = 'none';
    }
}

function cancelEdit() {
    // Hide inputs in profile form only - add hidden class
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.querySelectorAll('.profile-input').forEach(input => {
        input.classList.add('hidden');
        input.style.display = 'none';
    });
    }
    
    // Show static text
    const viewElements = ['view-username', 'view-email', 'view-phone', 'view-birthday', 
                         'view-address', 'view-city', 'view-country', 'view-postal'];
    viewElements.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.style.display = 'inline';
        }
    });
    
    // Hide buttons
    const formActions = document.getElementById('formActions');
    if (formActions) {
        formActions.classList.add('hidden');
        formActions.style.display = 'none';
    }
    
    // Show edit profile button specifically
    const editProfileBtn = document.getElementById('edit-profile-btn');
    if (editProfileBtn) {
        editProfileBtn.style.display = 'block';
    }
}

function toggleAddCard() {
    // If profile edit is open, close it first
    const formActions = document.getElementById('formActions');
    const editProfileBtn = document.getElementById('edit-profile-btn');
    if (formActions && !formActions.classList.contains('hidden') && formActions.style.display !== 'none') {
        cancelEdit();
    }
    
    // If password edit is open, close it first
    const passwordFields = document.getElementById('passwordFields');
    if (passwordFields && !passwordFields.classList.contains('hidden')) {
        cancelPasswordEdit();
    }
    
    const form = document.getElementById('add-card-form');
    const btn = document.getElementById('add-card-btn');
    if (!form || !btn) return;
    
    if (form.classList.contains('hidden') || form.style.display === 'none') {
        form.classList.remove('hidden');
        form.style.display = 'block';
        btn.style.display = 'none';
    } else {
        form.classList.add('hidden');
        form.style.display = 'none';
        btn.style.display = 'block';
    }
}

function togglePasswordEdit() {
    // If profile edit is open, close it first
    const formActions = document.getElementById('formActions');
    const editProfileBtn = document.getElementById('edit-profile-btn');
    if (formActions && !formActions.classList.contains('hidden') && formActions.style.display !== 'none') {
        cancelEdit();
    }
    
    // If add card form is open, close it first
    const addCardForm = document.getElementById('add-card-form');
    const addCardBtn = document.getElementById('add-card-btn');
    if (addCardForm && !addCardForm.classList.contains('hidden') && addCardForm.style.display !== 'none') {
        cancelAddCard();
    }
    
    const passwordFields = document.getElementById('passwordFields');
    const passwordFormActions = document.getElementById('passwordFormActions');
    const editPasswordBtn = document.getElementById('edit-password-btn');
    
    if (!passwordFields || !passwordFormActions || !editPasswordBtn) return;
    
    if (passwordFields.classList.contains('hidden')) {
        // Show password fields
        passwordFields.classList.remove('hidden');
        passwordFields.style.display = '';
        passwordFormActions.classList.remove('hidden');
        passwordFormActions.style.display = 'flex';
        editPasswordBtn.style.display = 'none';
    } else {
        // Hide password fields
        cancelPasswordEdit();
    }
}

function cancelPasswordEdit() {
    const passwordFields = document.getElementById('passwordFields');
    const passwordFormActions = document.getElementById('passwordFormActions');
    const editPasswordBtn = document.getElementById('edit-password-btn');
    const passwordForm = document.getElementById('passwordForm');
    
    if (passwordFields) {
        passwordFields.classList.add('hidden');
        passwordFields.style.display = 'none';
    }
    
    if (passwordFormActions) {
        passwordFormActions.classList.add('hidden');
        passwordFormActions.style.display = 'none';
    }
    
    if (editPasswordBtn) {
        editPasswordBtn.style.display = 'block';
    }
    
    // Reset form
    if (passwordForm) {
        passwordForm.reset();
    }
}

function cancelAddCard() {
    const addCardForm = document.getElementById('add-card-form');
    const addCardBtn = document.getElementById('add-card-btn');
    if (addCardForm) {
        addCardForm.classList.add('hidden');
        addCardForm.style.display = 'none';
    }
    if (addCardBtn) {
        addCardBtn.style.display = 'block';
    }
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

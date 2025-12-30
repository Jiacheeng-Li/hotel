/**
 * Keyboard Shortcuts Handler
 * 
 * Supports:
 * - g + h: Go to Home
 * - g + b: Go to Brands
 * - g + d: Go to Destinations
 * - g + a: Go to Account (login required)
 * - g + s: Go to My Stays (login required)
 * - g + k: Show keyboard shortcuts help
 * - s: Focus search bar
 * - ?: Show keyboard shortcuts help
 * - t: Start tour guide
 */

(function() {
    'use strict';

    // Shortcut state
    let firstKey = null;
    let firstKeyTimer = null;
    const SEQUENCE_TIMEOUT = 1000; // 1 second to complete sequence

    // URL mappings (will be set from template)
    const urls = {
        home: '/',
        brands: '/brands',
        destinations: '/destinations',
        account: '/account',
        my_stays: '/my_stays'
    };

    /**
     * Get URLs from data attributes or use defaults
     */
    function getUrls() {
        const body = document.body;
        return {
            home: body.dataset.urlHome || urls.home,
            brands: body.dataset.urlBrands || urls.brands,
            destinations: body.dataset.urlDestinations || urls.destinations,
            account: body.dataset.urlAccount || urls.account,
            my_stays: body.dataset.urlMyStays || urls.my_stays
        };
    }

    /**
     * Check if user is authenticated
     */
    function isAuthenticated() {
        // Check if there's a user dropdown or login button
        const userDropdown = document.getElementById('userDropdown');
        return userDropdown !== null;
    }

    /**
     * Navigate to a URL
     */
    function navigateTo(url) {
        if (url) {
            window.location.href = url;
        }
    }

    /**
     * Focus search input
     */
    function focusSearch() {
        // Try different search input selectors
        const searchSelectors = [
            'input[name="city"]',
            'input[name="destination"]',
            '#city',
            '#destination',
            'input[type="text"][placeholder*="Where"]',
            'input[type="text"][placeholder*="where"]',
            'input[type="text"][placeholder*="搜索"]',
            '.search-input',
            '#search-input'
        ];

        for (const selector of searchSelectors) {
            const input = document.querySelector(selector);
            if (input && input.offsetParent !== null) { // Check if visible
                input.focus();
                input.select();
                return true;
            }
        }

        return false;
    }

    /**
     * Show keyboard shortcuts modal
     */
    function showShortcutsModal() {
        const modal = document.getElementById('keyboard-shortcuts-modal');
        if (modal && typeof bootstrap !== 'undefined') {
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
        }
    }

    /**
     * Start tour guide
     */
    function startTour() {
        if (typeof window.startTourGuide === 'function') {
            window.startTourGuide();
        }
    }

    /**
     * Check if any modal/dialog is open or if we're on an auth page
     */
    function isModalOpen() {
        // Check for Bootstrap modals
        const bootstrapModals = document.querySelectorAll('.modal.show, .modal[style*="display"]');
        if (bootstrapModals.length > 0) {
            return true;
        }

        // Check for modal backdrop (Bootstrap)
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) {
            return true;
        }

        // Check for custom modals (celebration modal, etc.)
        const customModals = document.querySelectorAll('.celebration-modal.show, .retention-modal-content, [class*="modal"][class*="show"]');
        for (const modal of customModals) {
            const style = window.getComputedStyle(modal);
            if (style.display !== 'none' && style.visibility !== 'hidden') {
                return true;
            }
        }

        // Check if body has modal-open class (Bootstrap adds this)
        if (document.body.classList.contains('modal-open')) {
            return true;
        }

        // Check if we're on an auth page (login/register) - disable shortcuts there
        const authPage = document.querySelector('.auth-page, .auth-container, .auth-card');
        if (authPage) {
            return true;
        }

        return false;
    }

    /**
     * Reset shortcut sequence
     */
    function resetSequence() {
        firstKey = null;
        if (firstKeyTimer) {
            clearTimeout(firstKeyTimer);
            firstKeyTimer = null;
        }
    }

    /**
     * Handle keyboard events
     */
    function handleKeyDown(event) {
        // Check if any modal/dialog is open - if so, disable all shortcuts (except Esc)
        if (isModalOpen() && event.key !== 'Escape') {
            return;
        }

        // Check if user is typing in an input field
        const activeElement = document.activeElement;
        const isInputFocused = activeElement && (
            activeElement.tagName === 'INPUT' ||
            activeElement.tagName === 'TEXTAREA' ||
            activeElement.isContentEditable ||
            activeElement.closest('.modal')
        );

        // Don't handle shortcuts when typing in inputs (except for '?' and 'Esc')
        // Completely ignore all shortcuts when in any input/textarea to allow normal typing
        if (isInputFocused && event.key !== '?' && event.key !== 'Escape') {
            // Do not intercept any keys when user is typing in input fields
            // This allows normal typing of 's', 'g', etc. in forms
            return;
        }

        const key = event.key.toLowerCase();

        // Handle single key shortcuts
        switch (key) {
            case 's':
                // Focus search
                event.preventDefault();
                focusSearch();
                resetSequence();
                return;

            case '?':
                // Show shortcuts help
                event.preventDefault();
                showShortcutsModal();
                resetSequence();
                return;

            case 't':
                // Start tour guide
                event.preventDefault();
                startTour();
                resetSequence();
                return;
        }

        // Handle 'g' key sequences
        if (key === 'g') {
            if (firstKey === null) {
                // Start sequence
                firstKey = 'g';
                firstKeyTimer = setTimeout(() => {
                    resetSequence();
                }, SEQUENCE_TIMEOUT);
                event.preventDefault();
                return;
            }
        }

        // Handle second key in sequence (after 'g')
        if (firstKey === 'g') {
            event.preventDefault();
            clearTimeout(firstKeyTimer);
            
            const urls = getUrls();
            let shouldNavigate = false;
            let targetUrl = null;
            let handled = false;

            switch (key) {
                case 'h':
                    // Go to Home
                    targetUrl = urls.home;
                    shouldNavigate = true;
                    break;

                case 'b':
                    // Go to Brands
                    targetUrl = urls.brands;
                    shouldNavigate = true;
                    break;

                case 'd':
                    // Go to Destinations
                    targetUrl = urls.destinations;
                    shouldNavigate = true;
                    break;

                case 'a':
                    // Go to Account (login required)
                    if (isAuthenticated()) {
                        targetUrl = urls.account;
                        shouldNavigate = true;
                    } else {
                        // Redirect to login
                        window.location.href = '/login?next=' + encodeURIComponent(urls.account);
                        resetSequence();
                        return;
                    }
                    break;

                case 's':
                    // Go to My Stays (login required)
                    if (isAuthenticated()) {
                        targetUrl = urls.my_stays;
                        shouldNavigate = true;
                    } else {
                        // Redirect to login
                        window.location.href = '/login?next=' + encodeURIComponent(urls.my_stays);
                        resetSequence();
                        return;
                    }
                    break;

                case 'k':
                    // Show keyboard shortcuts
                    showShortcutsModal();
                    handled = true;
                    break;
            }

            if (shouldNavigate && targetUrl) {
                navigateTo(targetUrl);
            }

            if (!handled && !shouldNavigate) {
                // If key was not handled, reset sequence
                resetSequence();
            } else {
                resetSequence();
            }
        }
    }

    /**
     * Initialize keyboard shortcuts
     */
    function init() {
        document.addEventListener('keydown', handleKeyDown);
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose API for external use
    window.KeyboardShortcuts = {
        focusSearch: focusSearch,
        showShortcuts: showShortcutsModal,
        startTour: startTour
    };

})();


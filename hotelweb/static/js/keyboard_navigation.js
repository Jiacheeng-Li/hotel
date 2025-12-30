/**
 * Keyboard Navigation for Card-based Pages
 * 
 * Features:
 * - Press '/' to activate navigation mode
 * - Use arrow keys to navigate between cards
 * - Press Enter to open selected card
 * - Press Esc to exit navigation mode
 */

(function() {
    'use strict';

    // Navigation state
    let isActive = false;
    let currentIndex = -1;
    let cards = [];
    let navigationIndicator = null;

    // Card selectors for different page types (in priority order)
    const CARD_SELECTORS = [
        '.booking-card',                    // Booking cards (my stays) - highest priority
        '.hotel-card',                      // Hotel cards (destinations, brand detail, etc.)
        '#list-view .card.mb-4.shadow-sm', // Search results cards (more specific)
        '.card.hotel-card',                 // Alternative hotel card selector
        '.card.mb-4.shadow-sm'              // Fallback for search results
    ];

    /**
     * Find all navigable cards on the page
     */
    function findCards() {
        cards = [];
        
        // Try each selector in priority order
        for (const selector of CARD_SELECTORS) {
            try {
                const found = document.querySelectorAll(selector);
                if (found.length > 0) {
                    // Filter out cards that are hidden or in hidden containers
                    found.forEach(card => {
                        if (isCardVisible(card)) {
                            cards.push(card);
                        }
                    });
                    // If we found cards with this selector, use them
                    if (cards.length > 0) {
                        break;
                    }
                }
            } catch (e) {
                // Invalid selector, skip
                console.warn('Invalid card selector:', selector, e);
            }
        }

        return cards;
    }

    /**
     * Check if a card is visible
     */
    function isCardVisible(card) {
        const style = window.getComputedStyle(card);
        if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
            return false;
        }
        
        // Check if parent containers are visible
        let parent = card.parentElement;
        while (parent && parent !== document.body) {
            const parentStyle = window.getComputedStyle(parent);
            if (parentStyle.display === 'none' || parentStyle.visibility === 'hidden') {
                return false;
            }
            parent = parent.parentElement;
        }
        
        return true;
    }

    /**
     * Find the link within a card to navigate to
     */
    function findCardLink(card) {
        // Priority order for finding links:
        // 1. Links to hotel_detail or roomtype_detail (main content links)
        // 2. "View" or "View Details" button
        // 3. Main title link (excluding brand links)
        // 4. Any other link (excluding brand links and # links)
        
        // First, try to find hotel/room detail links (highest priority)
        const allLinks = card.querySelectorAll('a[href]');
        for (const link of allLinks) {
            if (link.href && (
                link.href.includes('/hotel_detail') || 
                link.href.includes('/roomtype_detail') ||
                link.href.includes('hotel_detail') ||
                link.href.includes('roomtype_detail')
            )) {
                return link;
            }
        }

        // Try to find view button (usually links to hotel detail)
        const viewButton = card.querySelector('a.btn-primary, a.btn, .view-details, a[href*="hotel_detail"], a[href*="roomtype_detail"]');
        if (viewButton && viewButton.href && !viewButton.href.includes('brand_detail')) {
            return viewButton;
        }

        // Try to find title link, but exclude brand links
        const titleLinks = card.querySelectorAll('h3 a, h4 a, h5 a, .hotel-name a, .booking-details a, .hotel-card-title a');
        for (const link of titleLinks) {
            if (link.href && !link.href.includes('brand_detail') && !link.href.includes('#')) {
                return link;
            }
        }

        // Last resort: find any link excluding brand links and # links
        for (const link of allLinks) {
            if (link.href && 
                !link.href.includes('#') && 
                !link.href.includes('brand_detail') &&
                !link.classList.contains('brand-badge') &&
                !link.classList.contains('hotel-brand-badge')) {
                return link;
            }
        }

        return null;
    }

    /**
     * Create navigation indicator
     */
    function createIndicator() {
        if (navigationIndicator) {
            return navigationIndicator;
        }

        const indicator = document.createElement('div');
        indicator.id = 'keyboard-nav-indicator';
        indicator.className = 'keyboard-nav-indicator';
        indicator.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            padding: 10px 18px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            z-index: 10000;
            display: none;
            pointer-events: none;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            animation: slideInRight 0.3s ease-out;
        `;
        indicator.innerHTML = '<span style="margin-right: 8px;">⌨️</span>Navigation Mode Active';
        document.body.appendChild(indicator);
        navigationIndicator = indicator;
        return indicator;
    }

    /**
     * Show navigation indicator
     */
    function showIndicator() {
        const indicator = createIndicator();
        indicator.style.display = 'block';
    }

    /**
     * Hide navigation indicator
     */
    function hideIndicator() {
        if (navigationIndicator) {
            navigationIndicator.style.display = 'none';
        }
    }

    /**
     * Highlight a card
     */
    function highlightCard(index) {
        // Remove previous highlight
        cards.forEach(card => {
            card.classList.remove('keyboard-nav-active');
            card.style.outline = '';
            card.style.outlineOffset = '';
            card.style.transform = '';
        });

        if (index >= 0 && index < cards.length) {
            const card = cards[index];
            card.classList.add('keyboard-nav-active');
            card.style.outline = '3px solid #3b82f6';
            card.style.outlineOffset = '2px';
            card.style.transform = 'scale(1.02)';
            
            // Scroll card into view with some padding
            const cardRect = card.getBoundingClientRect();
            const isAboveViewport = cardRect.top < 0;
            const isBelowViewport = cardRect.bottom > window.innerHeight;
            
            if (isAboveViewport || isBelowViewport) {
                card.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    }

    /**
     * Activate navigation mode
     */
    function activateNavigation() {
        if (isActive) {
            return;
        }

        cards = findCards();
        
        if (cards.length === 0) {
            // No cards found, show brief message
            const indicator = createIndicator();
            indicator.innerHTML = '<span style="margin-right: 8px;">ℹ️</span>No cards found on this page';
            indicator.style.display = 'block';
            setTimeout(() => {
                indicator.style.display = 'none';
            }, 2000);
            return;
        }

        isActive = true;
        currentIndex = 0;
        highlightCard(currentIndex);
        showIndicator();

        // Add active class to body for CSS styling
        document.body.classList.add('keyboard-nav-mode');
    }

    /**
     * Deactivate navigation mode
     */
    function deactivateNavigation() {
        if (!isActive) {
            return;
        }

        isActive = false;
        currentIndex = -1;
        highlightCard(-1);
        hideIndicator();
        document.body.classList.remove('keyboard-nav-mode');
    }

    /**
     * Navigate to next card
     */
    function navigateNext() {
        if (!isActive || cards.length === 0) {
            return;
        }
        currentIndex = (currentIndex + 1) % cards.length;
        highlightCard(currentIndex);
    }

    /**
     * Navigate to previous card
     */
    function navigatePrevious() {
        if (!isActive || cards.length === 0) {
            return;
        }
        currentIndex = (currentIndex - 1 + cards.length) % cards.length;
        highlightCard(currentIndex);
    }

    /**
     * Calculate cards per row based on layout
     */
    function calculateCardsPerRow() {
        if (cards.length === 0) return 1;

        const firstCard = cards[0];
        const cardRect = firstCard.getBoundingClientRect();
        const container = firstCard.closest('.row, .container, [class*="row-cols"]');
        
        if (!container) return 1;

        // Check for Bootstrap row-cols classes
        const rowColsClasses = ['row-cols-1', 'row-cols-md-2', 'row-cols-md-3', 'row-cols-md-4', 'row-cols-lg-3', 'row-cols-lg-4'];
        for (const cls of rowColsClasses) {
            if (container.classList.contains(cls)) {
                // Extract number from class (e.g., "row-cols-md-3" -> 3)
                const match = cls.match(/(\d+)$/);
                if (match) {
                    return parseInt(match[1]);
                }
            }
        }

        // Calculate based on container width and card width
        const containerRect = container.getBoundingClientRect();
        const gap = 16; // Typical gap between cards
        const cardWidthWithGap = cardRect.width + gap;
        const cardsPerRow = Math.floor((containerRect.width + gap) / cardWidthWithGap) || 1;
        
        return Math.max(1, cardsPerRow);
    }

    /**
     * Navigate based on arrow key direction
     */
    function navigate(direction) {
        if (!isActive || cards.length === 0) {
            return;
        }

        const cardsPerRow = calculateCardsPerRow();
        
        switch (direction) {
            case 'ArrowRight':
                if (currentIndex < cards.length - 1) {
                    currentIndex = Math.min(currentIndex + 1, cards.length - 1);
                }
                break;
            case 'ArrowLeft':
                if (currentIndex > 0) {
                    currentIndex = Math.max(currentIndex - 1, 0);
                }
                break;
            case 'ArrowDown':
                const nextRowIndex = currentIndex + cardsPerRow;
                if (nextRowIndex < cards.length) {
                    currentIndex = nextRowIndex;
                } else {
                    // If can't go down, go to last card
                    currentIndex = cards.length - 1;
                }
                break;
            case 'ArrowUp':
                const prevRowIndex = currentIndex - cardsPerRow;
                if (prevRowIndex >= 0) {
                    currentIndex = prevRowIndex;
                } else {
                    // If can't go up, go to first card
                    currentIndex = 0;
                }
                break;
        }

        highlightCard(currentIndex);
    }

    /**
     * Open selected card
     */
    function openCard() {
        if (!isActive || currentIndex < 0 || currentIndex >= cards.length) {
            return;
        }

        const card = cards[currentIndex];
        const link = findCardLink(card);

        if (link) {
            link.click();
        } else {
            // If no link found, try to make card clickable
            card.click();
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

        // Check if we're on an auth page (login/register) - disable navigation there
        const authPage = document.querySelector('.auth-page, .auth-container, .auth-card');
        if (authPage) {
            return true;
        }

        return false;
    }

    /**
     * Handle keyboard events
     */
    function handleKeyDown(event) {
        // Check if any modal/dialog is open - if so, disable navigation (except Esc to exit)
        if (isModalOpen() && event.key !== 'Escape') {
            // If navigation was active, deactivate it when modal opens
            if (isActive) {
                deactivateNavigation();
            }
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

        // Activate navigation with '/' key (but not when typing in inputs)
        // Only activate if not in a search input or text field
        if (event.key === '/' && !isInputFocused) {
            // Check if we're on a page with cards
            const hasCards = findCards().length > 0;
            if (hasCards) {
                event.preventDefault();
                event.stopPropagation();
                if (isActive) {
                    deactivateNavigation();
                } else {
                    activateNavigation();
                }
                return;
            }
        }

        // Only handle navigation keys when active
        if (!isActive) {
            return;
        }

        // Prevent default for navigation keys
        if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Enter', 'Escape'].includes(event.key)) {
            event.preventDefault();
        }

        switch (event.key) {
            case 'ArrowUp':
            case 'ArrowDown':
            case 'ArrowLeft':
            case 'ArrowRight':
                navigate(event.key);
                break;
            case 'Enter':
                openCard();
                break;
            case 'Escape':
                deactivateNavigation();
                break;
        }
    }

    /**
     * Initialize keyboard navigation
     */
    function init() {
        // Add event listener
        document.addEventListener('keydown', handleKeyDown);

        // Re-find cards when page content changes (for dynamic content)
        // Use debounce to avoid excessive re-searching
        let debounceTimer;
        const observer = new MutationObserver(() => {
            if (isActive) {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    const oldCount = cards.length;
                    cards = findCards();
                    // If card count changed, reset index
                    if (cards.length !== oldCount) {
                        currentIndex = Math.min(currentIndex, cards.length - 1);
                        if (currentIndex >= 0 && currentIndex < cards.length) {
                            highlightCard(currentIndex);
                        } else if (cards.length > 0) {
                            currentIndex = 0;
                            highlightCard(currentIndex);
                        } else {
                            deactivateNavigation();
                        }
                    }
                }, 300);
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        // Add CSS for active card highlight
        if (!document.getElementById('keyboard-nav-styles')) {
            const style = document.createElement('style');
            style.id = 'keyboard-nav-styles';
            style.textContent = `
                .keyboard-nav-active {
                    position: relative;
                    z-index: 10;
                    transition: transform 0.2s ease, box-shadow 0.2s ease;
                }
                .keyboard-nav-active::before {
                    content: '';
                    position: absolute;
                    top: -3px;
                    left: -3px;
                    right: -3px;
                    bottom: -3px;
                    border: 3px solid #3b82f6;
                    border-radius: 8px;
                    pointer-events: none;
                    z-index: 11;
                    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
                }
                @keyframes slideInRight {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose API for external use
    window.KeyboardNavigation = {
        activate: activateNavigation,
        deactivate: deactivateNavigation,
        isActive: () => isActive
    };

})();

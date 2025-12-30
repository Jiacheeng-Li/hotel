/**
 * Language Switching Functionality
 * Handles language preference management and UI updates
 */

(function() {
    'use strict';

    // Language storage key for localStorage
    const LANGUAGE_STORAGE_KEY = 'user_language_preference';

    /**
     * Get current language from localStorage or return null
     */
    function getStoredLanguage() {
        try {
            return localStorage.getItem(LANGUAGE_STORAGE_KEY);
        } catch (e) {
            // localStorage might not be available
            return null;
        }
    }

    /**
     * Store language preference to localStorage
     */
    function storeLanguage(langCode) {
        try {
            localStorage.setItem(LANGUAGE_STORAGE_KEY, langCode);
        } catch (e) {
            // localStorage might not be available, ignore
            console.warn('Could not store language preference:', e);
        }
    }

    /**
     * Initialize language switcher
     */
    function initLanguageSwitcher() {
        const languageDropdown = document.getElementById('languageDropdown');
        if (!languageDropdown) return;

        // Find the dropdown menu (it's a sibling ul element after the languageDropdown anchor)
        // Also try finding it by aria-labelledby relationship for robustness
        const dropdownMenu = languageDropdown.nextElementSibling || 
                           document.querySelector('ul[aria-labelledby="languageDropdown"]');
        if (!dropdownMenu) return;

        const languageLinks = dropdownMenu.querySelectorAll('.dropdown-item');
        
        // Add click handlers to language links
        languageLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (!href || href === '#') return;

                // Get language code from URL
                const langMatch = href.match(/\/set_language\/([^\/]+)/);
                if (!langMatch) return;

                const langCode = langMatch[1];
                
                // Store language preference
                storeLanguage(langCode);

                // Add visual feedback - show loading state
                const languageCode = languageDropdown.querySelector('.language-code');
                if (languageCode) {
                    languageCode.textContent = '...';
                    languageCode.style.opacity = '0.5';
                }

                // The page will redirect after language is set, so we don't need to prevent default
                // Allow the default link behavior to proceed
            });
        });
    }

    /**
     * Sync language preference on page load
     * This can be used to restore language from localStorage if needed
     */
    function syncLanguagePreference() {
        // Note: The server-side session takes precedence
        // This is mainly for future enhancements or client-side only features
        const storedLang = getStoredLanguage();
        if (storedLang) {
            // You could implement client-side language switching here if needed
            // For now, server-side session management is used
        }
    }

    /**
     * Update language code display
     */
    function updateLanguageDisplay(langCode) {
        const languageCode = document.querySelector('#languageDropdown .language-code');
        if (languageCode && langCode) {
            languageCode.textContent = langCode.toUpperCase();
        }
    }

    /**
     * Get current language from the page
     */
    function getCurrentLanguage() {
        const languageCode = document.querySelector('#languageDropdown .language-code');
        if (languageCode) {
            return languageCode.textContent.toLowerCase();
        }
        return null;
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            initLanguageSwitcher();
            syncLanguagePreference();
        });
    } else {
        // DOM is already loaded
        initLanguageSwitcher();
        syncLanguagePreference();
    }

    // Expose public API if needed
    window.LanguageSwitcher = {
        getCurrentLanguage: getCurrentLanguage,
        getStoredLanguage: getStoredLanguage,
        storeLanguage: storeLanguage,
        updateLanguageDisplay: updateLanguageDisplay
    };

})();

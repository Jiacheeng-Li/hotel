// Tour Guide - Interactive User Onboarding
// Provides step-by-step guidance for key features

(function() {
    'use strict';

    // Tour steps configuration
    const tourSteps = {
        home: [
            {
                element: '.home-search-card',
                intro: '<h3>Search Hotels</h3><p>Enter your destination, check-in and check-out dates here, then click "Search" to find the perfect hotel for your stay.</p>',
                position: 'bottom'
            },
            {
                element: '.navbar-nav',
                intro: '<h3>Navigation Menu</h3><p>Use the top navigation bar to quickly access: Home, Brands, Destinations, and more. After logging in, you can also view "My Account" and "My Stays".</p>',
                position: 'bottom'
            },
            {
                element: '.hero-text-container',
                intro: '<h3>Welcome to Lumina</h3><p>Explore our curated collection of luxury hotel brands worldwide and experience extraordinary stays.</p>',
                position: 'bottom'
            }
        ],
        search: [
            {
                element: '.search-sidebar-card',
                intro: '<h3>Filters & Sorting</h3><p>Use the filters on the left to narrow down your search, or use the sort function to organize results by price, rating, and more.</p>',
                position: 'right'
            },
            {
                element: '.search-hotel-card-body',
                intro: '<h3>Hotel Cards</h3><p>Click on a hotel card to view detailed information including room types, amenities, and location. You can also click the heart icon in the top-right corner to favorite a hotel.</p>',
                position: 'top'
            },
            {
                element: '#map-tab',
                intro: '<h3>Map View</h3><p>Switch to map view to see hotel locations on a map, helping you choose the most convenient location.</p>',
                position: 'bottom'
            }
        ],
        account: [
            {
                element: '.account-header',
                intro: '<h3>Membership Information</h3><p>Here you can see your membership tier, member number, and current points balance. Different tiers enjoy different membership benefits.</p>',
                position: 'bottom'
            },
            {
                element: '.account-nav',
                intro: '<h3>Account Navigation</h3><p>Use these tabs to view: Current Status, Milestone Rewards, Account Activity, My Stays, and Settings.</p>',
                position: 'bottom'
            },
            {
                element: '.points-value',
                intro: '<h3>Points System</h3><p>Earn points by booking stays. Points can be redeemed for free nights, room upgrades, or breakfast vouchers.</p>',
                position: 'left'
            }
        ],
        hotelDetail: [
            {
                element: '#hotel-main-image',
                intro: '<h3>Hotel Details</h3><p>View high-quality images, detailed descriptions, location information, and amenities list for the hotel.</p>',
                position: 'bottom'
            },
            {
                element: '.btn-favorite',
                intro: '<h3>Favorite Feature</h3><p>Click the heart icon to favorite this hotel for easy access later. Favorited hotels will appear in the "Favorites" tab on your "My Stays" page.</p>',
                position: 'left'
            },
            {
                element: '.room-type-card',
                intro: '<h3>Select Room</h3><p>Browse available room types, view prices, capacity, and amenities, then click "View Details" to see more information and make a booking.</p>',
                position: 'top'
            }
        ],
        myStays: [
            {
                element: '.stays-tabs',
                intro: '<h3>My Stays</h3><p>Use these tabs to view: Upcoming bookings, Current stays, Past history, Favorited hotels, and Special events.</p>',
                position: 'bottom'
            },
            {
                element: '.booking-card',
                intro: '<h3>Booking Management</h3><p>View your booking details including check-in dates, room information, and total cost. For completed stays, you can write a review.</p>',
                position: 'top'
            },
            {
                element: '.favorite-hotel-card',
                intro: '<h3>Favorited Hotels</h3><p>Here you can see all your favorited hotels. Click on a hotel card to view details or make a booking directly.</p>',
                position: 'top'
            }
        ]
    };

    // Get current page type
    function getCurrentPageType() {
        const path = window.location.pathname;
        if (path === '/' || path.includes('index')) {
            return 'home';
        } else if (path.includes('search')) {
            return 'search';
        } else if (path.includes('account')) {
            return 'account';
        } else if (path.includes('hotel') && path.match(/\d+/)) {
            return 'hotelDetail';
        } else if (path.includes('my_stays')) {
            return 'myStays';
        }
        return null;
    }

    // Start tour for current page
    function startTour() {
        // Scroll to top first, then start the tour
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });

        // Wait for scroll animation to complete before starting tour
        setTimeout(function() {
            const pageType = getCurrentPageType();
            let steps = [];
            
            if (!pageType || !tourSteps[pageType]) {
                // Generic tour if page type not found
                steps = [
                    {
                        intro: '<h3>Welcome to Lumina Hotel Booking System</h3><p>This is a quick guide to help you understand how to use our website. Click "Next" to continue.</p>'
                    },
                    {
                        element: '.navbar',
                        intro: '<h3>Navigation Bar</h3><p>Use the top navigation bar to access the main features of the website. After logging in, you can view your personal account and booking information.</p>',
                        position: 'bottom'
                    },
                    {
                        element: 'footer',
                        intro: '<h3>Need Help?</h3><p>You can always click the "Tour Guide" link in the footer to view this guide again. Enjoy your stay!</p>',
                        position: 'top'
                    }
                ];
            } else {
                steps = tourSteps[pageType].map(step => {
                    // Check if element exists
                    const element = document.querySelector(step.element);
                    if (!element) {
                        return null;
                    }
                    return step;
                }).filter(step => step !== null);
            }

            if (steps.length === 0) {
                alert('Sorry, there are no available tour steps for this page.');
                return;
            }

            // Create intro.js instance
            const intro = introJs();
            
            intro.setOptions({
                steps: steps,
                showProgress: true,
                showBullets: true,
                exitOnOverlayClick: true,
                exitOnEsc: true,
                nextLabel: 'Next',
                prevLabel: 'Previous',
                skipLabel: 'Skip',
                doneLabel: 'Done',
                tooltipClass: 'customTooltip',
                highlightClass: 'customHighlight'
            });

            intro.start();
        }, 500); // Wait 500ms for smooth scroll to complete
    }

    // Initialize tour guide
    document.addEventListener('DOMContentLoaded', function() {
        // Add click handler to tour guide link
        const tourLink = document.getElementById('tour-guide-link');
        if (tourLink) {
            tourLink.addEventListener('click', function(e) {
                e.preventDefault();
                startTour();
            });
        }

        // Check if this is first visit (optional - can be enhanced with localStorage)
        // For now, we'll just make it available via the footer link
    });

    // Make startTour available globally for potential future use
    window.startTourGuide = startTour;

})();


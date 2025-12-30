// Write Review Logic

// Initialize review data from data attribute
function initializeReviewData() {
    const dataElement = document.querySelector('.review-data');
    if (dataElement) {
        try {
            const initialRatingStr = dataElement.getAttribute('data-initial-rating');
            window.reviewData = {
                initialRating: initialRatingStr === 'null' ? null : parseInt(initialRatingStr)
            };
        } catch (e) {
            console.error('Error parsing review data:', e);
            window.reviewData = {
                initialRating: null
            };
        }
    } else {
        window.reviewData = {
            initialRating: null
        };
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize data first
    initializeReviewData();
    
    const ratingInputs = document.querySelectorAll('input[name="rating"]');
    const ratingText = document.getElementById('rating-text');
    const ratingLabels = document.querySelectorAll('.rating-star');
    
    const ratingTexts = {
        1: 'Poor',
        2: 'Fair',
        3: 'Good',
        4: 'Very Good',
        5: 'Excellent'
    };
    
    // Initialize rating display if existing review
    if (window.reviewData && window.reviewData.initialRating) {
        const initialRating = window.reviewData.initialRating;
        if (ratingText) {
            ratingText.textContent = ratingTexts[initialRating];
        }
        ratingLabels.forEach((label, index) => {
            if (index < initialRating) {
                label.classList.add('rating-selected');
            } else {
                label.classList.remove('rating-selected');
            }
        });
    }
    
    ratingInputs.forEach(input => {
        input.addEventListener('change', function() {
            const rating = parseInt(this.value);
            if (ratingText) {
                ratingText.textContent = ratingTexts[rating];
            }
            
            // Update star colors using CSS classes
            ratingLabels.forEach((label, index) => {
                if (index < rating) {
                    label.classList.add('rating-selected');
                } else {
                    label.classList.remove('rating-selected');
                }
            });
        });
        
        // Hover effect
        const label = input.parentElement;
        label.addEventListener('mouseover', function() {
            const hoverRating = parseInt(input.value);
            ratingLabels.forEach((l, index) => {
                if (index < hoverRating) {
                    l.classList.add('rating-hover');
                }
            });
        });
        
        label.addEventListener('mouseout', function() {
            // Remove hover class from all labels
            ratingLabels.forEach(l => {
                l.classList.remove('rating-hover');
            });
            
            // Revert to selected state
            const checkedInput = document.querySelector('input[name="rating"]:checked');
            const currentRating = checkedInput ? parseInt(checkedInput.value) : 0;
            
            ratingLabels.forEach((l, index) => {
                if (index < currentRating) {
                    l.classList.add('rating-selected');
                } else {
                    l.classList.remove('rating-selected');
                }
            });
        });
    });
});


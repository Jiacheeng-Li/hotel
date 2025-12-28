// Write Review Logic
document.addEventListener('DOMContentLoaded', function() {
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
        ratingText.textContent = ratingTexts[initialRating];
        ratingLabels.forEach((label, index) => {
            if (index < initialRating) {
                label.style.color = '#dc3545'; // Red for selected
            } else {
                label.style.color = '#ddd'; // Gray for unselected
            }
        });
    }
    
    ratingInputs.forEach(input => {
        input.addEventListener('change', function() {
            const rating = parseInt(this.value);
            ratingText.textContent = ratingTexts[rating];
            
            // Update star colors
            ratingLabels.forEach((label, index) => {
                if (index < rating) {
                    label.style.color = '#dc3545'; // Red for selected
                } else {
                    label.style.color = '#ddd'; // Gray for unselected
                }
            });
        });
        
        // Hover effect
        const label = input.parentElement;
        label.addEventListener('mouseover', function() {
            const hoverRating = parseInt(input.value);
            ratingLabels.forEach((l, index) => {
                if (index < hoverRating) {
                    l.style.color = '#ffc107'; // Yellow on hover
                }
            });
        });
        
        label.addEventListener('mouseout', function() {
            // Revert to selected state
            const checkedInput = document.querySelector('input[name="rating"]:checked');
            const currentRating = checkedInput ? parseInt(checkedInput.value) : 0;
            
            ratingLabels.forEach((l, index) => {
                if (index < currentRating) {
                    l.style.color = '#dc3545';
                } else {
                    l.style.color = '#ddd';
                }
            });
        });
    });
});


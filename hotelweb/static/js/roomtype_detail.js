// Room Type Detail Page Logic

document.addEventListener('DOMContentLoaded', function() {
    const breakfastCheckbox = document.getElementById('breakfast_included');
    const pointsDisplayNumber = document.querySelector('.points-display-number');
    
    if (!breakfastCheckbox) return;
    
    // Get base values from window.roomData (set by template)
    if (!window.roomData) return;
    
    const basePricePerNight = window.roomData.basePricePerNight;
    const taxRate = 0.10;
    const serviceFeeRate = 0.05;
    const breakfastPricePerRoom = window.roomData.breakfastPricePerRoom;
    const basePointsPerNight = window.roomData.basePointsPerNight || 0;
    const multiplier = window.roomData.multiplier || 1;
    
    // Calculate base price with tax
    const basePriceWithTax = basePricePerNight * (1 + taxRate + serviceFeeRate);
    
    // Calculate points per dollar (10 points per $1)
    const pointsPerDollar = 10;
    
    function updatePriceAndPoints() {
        const breakfastIncluded = breakfastCheckbox.checked;
        
        // Update main price (per night)
        const pricePerNightElement = document.getElementById('price-per-night');
        if (pricePerNightElement) {
            let newPricePerNight = basePricePerNight;
            if (breakfastIncluded) {
                // Add breakfast price per room per stay (not per night, but we'll add it to show total)
                newPricePerNight = basePricePerNight + breakfastPricePerRoom;
            }
            pricePerNightElement.textContent = '$' + Math.round(newPricePerNight).toLocaleString();
        }
        
        // Update price with tax
        const priceWithTaxElement = document.getElementById('price-with-tax');
        if (priceWithTaxElement) {
            let newPriceWithTax = basePriceWithTax;
            if (breakfastIncluded) {
                // Add breakfast price per room per stay (not per night)
                newPriceWithTax = basePriceWithTax + breakfastPricePerRoom;
            }
            priceWithTaxElement.textContent = '$' + newPriceWithTax.toFixed(2) + ' incl. tax';
        }
        
        // Update points
        if (pointsDisplayNumber && basePointsPerNight > 0) {
            let newPointsPerNight = basePointsPerNight;
            if (breakfastIncluded) {
                // Add points from breakfast: breakfast_price * pointsPerDollar * multiplier
                const breakfastPoints = Math.floor(breakfastPricePerRoom * pointsPerDollar * multiplier);
                newPointsPerNight = basePointsPerNight + breakfastPoints;
            }
            pointsDisplayNumber.textContent = newPointsPerNight.toLocaleString();
        }
    }
    
    // Add event listener
    breakfastCheckbox.addEventListener('change', updatePriceAndPoints);
});


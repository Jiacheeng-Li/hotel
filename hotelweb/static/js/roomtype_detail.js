// Room Type Detail Page Logic

// Initialize room data from data attribute
function initializeRoomData() {
    const dataElement = document.querySelector('.roomtype-data');
    if (dataElement) {
        try {
            window.roomData = {
                basePricePerNight: parseFloat(dataElement.getAttribute('data-base-price')) || 0,
                breakfastPricePerRoom: parseFloat(dataElement.getAttribute('data-breakfast-price')) || 0,
                basePointsPerNight: parseInt(dataElement.getAttribute('data-base-points')) || 0,
                multiplier: parseFloat(dataElement.getAttribute('data-multiplier')) || 1
            };
        } catch (e) {
            console.error('Error parsing room data:', e);
            window.roomData = {
                basePricePerNight: 0,
                breakfastPricePerRoom: 0,
                basePointsPerNight: 0,
                multiplier: 1
            };
        }
    } else {
        window.roomData = {
            basePricePerNight: 0,
            breakfastPricePerRoom: 0,
            basePointsPerNight: 0,
            multiplier: 1
        };
    }
}

// Update check-out minimum date based on check-in date
function updateCheckOutMin() {
    const checkInInput = document.getElementById('check_in');
    const checkOutInput = document.getElementById('check_out');
    if (checkInInput && checkInInput.value && checkOutInput) {
        const checkInDate = new Date(checkInInput.value);
        checkInDate.setDate(checkInDate.getDate() + 1);
        const minCheckOut = checkInDate.toISOString().split('T')[0];
        checkOutInput.min = minCheckOut;
        
        // If current check-out is before new minimum, update it
        if (checkOutInput.value && checkOutInput.value < minCheckOut) {
            checkOutInput.value = minCheckOut;
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize data first
    initializeRoomData();
    
    const breakfastCheckbox = document.getElementById('breakfast_included');
    const pointsDisplayNumber = document.querySelector('.points-display-number');
    
    if (!breakfastCheckbox) return;
    
    // Get base values from window.roomData
    if (!window.roomData) return;
    
    const basePricePerNight = window.roomData.basePricePerNight;
    const taxRate = 0.10;
    const serviceFeeRate = 0.05;
    const breakfastPricePerRoom = window.roomData.breakfastPricePerRoom;
    const basePointsPerNight = window.roomData.basePointsPerNight || 0;
    const multiplier = window.roomData.multiplier || 1;
    
    // Set up check-in date change listener
    const checkInInput = document.getElementById('check_in');
    if (checkInInput) {
        checkInInput.addEventListener('change', updateCheckOutMin);
        checkInInput.addEventListener('input', updateCheckOutMin);
    }
    
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


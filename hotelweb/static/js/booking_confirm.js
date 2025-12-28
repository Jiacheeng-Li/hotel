// Booking Confirmation Logic

function calculatePointsEarned(paymentAmount) {
    if (paymentAmount <= 0) return 0;
    // Formula: 1 dollar = 10 base points, then multiply by tier multiplier
    const perNightTotal = window.bookingData.baseRate * 1.15;  // Room rate with taxes/fees equivalent
    const basePointsPerNight = Math.floor(perNightTotal * 10);  // 10 points per $1
    const pointsPerNight = Math.floor(basePointsPerNight * window.bookingData.multiplier);
    return pointsPerNight * window.bookingData.nights * window.bookingData.roomsNeeded;
}

function updateBreakfastPrice() {
    const voucherRadios = document.querySelectorAll('input[name="breakfast_voucher_id"]');
    const breakfastPriceSpan = document.querySelector('.breakfast-price');
    const breakfastRow = document.querySelector('.breakfast-row');
    
    let selectedVoucher = null;
    for (const radio of voucherRadios) {
        if (radio.checked && radio.value) {
            selectedVoucher = radio.value;
            break;
        }
    }
    
    let currentBreakfastTotal = 0;
    if (window.bookingData.breakfastIncluded) {
        if (selectedVoucher) {
            // Using voucher - breakfast is free
            currentBreakfastTotal = 0;
            if (breakfastPriceSpan) {
                breakfastPriceSpan.innerHTML = '<span class="text-decoration-line-through text-muted">$' + window.bookingData.breakfastPrice.toFixed(2) + '</span> <span class="text-success ms-2">$0.00</span>';
            }
        } else {
            // Paying for breakfast
            currentBreakfastTotal = window.bookingData.breakfastPrice;
            if (breakfastPriceSpan) {
                breakfastPriceSpan.textContent = '$' + window.bookingData.breakfastPrice.toFixed(2);
            }
        }
    }
    
    // Update total
    const newTotal = window.bookingData.baseTotal + currentBreakfastTotal;
    updateTotalAndPoints(newTotal);
}

function updateTotalAndPoints(newTotal) {
    const totalDisplay = document.getElementById('total_display');
    const priceBreakdownTotal = document.getElementById('price-breakdown-total');
    const pointsEarnedDisplay = document.getElementById('points-earned-display');
    const pointsEarnedCard = document.getElementById('points-earned-card');
    
    // Check payment method
    const payWithPoints = document.getElementById('pay_with_points');
    const payNow = document.getElementById('pay_now');
    const payAtHotel = document.getElementById('pay_at_hotel');
    
    let actualPaymentAmount = newTotal;
    let pointsEarned = 0;
    
    if (payWithPoints && payWithPoints.checked) {
        // If paying with points, calculate remaining balance
        const pointsNeeded = Math.ceil(newTotal * window.bookingData.pointsPerDollar);
        const remainingBalance = Math.max(0, newTotal - (window.bookingData.userPoints / window.bookingData.pointsPerDollar));
        actualPaymentAmount = remainingBalance;
        
        // Points are only earned on actual payment (not on points payment)
        pointsEarned = calculatePointsEarned(remainingBalance);
    } else {
        // Paying with cash/card - earn points on full amount
        pointsEarned = calculatePointsEarned(newTotal);
    }
    
    // Update total display
    if (totalDisplay) {
        if (payWithPoints && payWithPoints.checked) {
            const pointsNeeded = Math.ceil(newTotal * window.bookingData.pointsPerDollar);
            if (window.bookingData.userPoints >= pointsNeeded) {
                totalDisplay.textContent = '$0.00 (Paid with Points)';
                totalDisplay.className = 'fw-bold fs-5 text-success';
            } else {
                const remainingBalance = Math.max(0, newTotal - (window.bookingData.userPoints / window.bookingData.pointsPerDollar));
                totalDisplay.textContent = '$' + remainingBalance.toFixed(2);
                totalDisplay.className = 'fw-bold fs-5 text-warning';
            }
        } else {
            totalDisplay.textContent = '$' + newTotal.toFixed(2);
            totalDisplay.className = 'fw-bold fs-5 text-success';
        }
    }
    
    // Update price breakdown total
    if (priceBreakdownTotal) {
        priceBreakdownTotal.textContent = '$' + newTotal.toFixed(2);
    }
    
    // Update points earned display
    if (pointsEarnedDisplay) {
        pointsEarnedDisplay.textContent = pointsEarned.toLocaleString() + ' points';
    }
    
    if (pointsEarnedCard) {
        if (pointsEarned > 0) {
            pointsEarnedCard.style.display = 'block';
        } else {
            pointsEarnedCard.style.display = 'none';
        }
    }
    
    // Update payment method info
    updatePaymentMethod(newTotal);
}

function updatePaymentMethod(newTotal) {
    const payWithPoints = document.getElementById('pay_with_points');
    const pointsInfo = document.getElementById('points_payment_info');
    const pointsNeededSpan = document.getElementById('points_needed');
    const remainingBalanceSpan = document.getElementById('remaining_balance');
    
    if (payWithPoints && payWithPoints.checked) {
        if (pointsInfo) pointsInfo.style.display = 'block';
        const pointsNeeded = Math.ceil(newTotal * window.bookingData.pointsPerDollar);
        const remainingBalance = Math.max(0, newTotal - (window.bookingData.userPoints / window.bookingData.pointsPerDollar));
        
        if (pointsNeededSpan) pointsNeededSpan.textContent = pointsNeeded.toLocaleString();
        if (remainingBalanceSpan) remainingBalanceSpan.textContent = '$' + remainingBalance.toFixed(2);
    } else {
        if (pointsInfo) pointsInfo.style.display = 'none';
    }
}

// Initialization on load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize payment method handlers
    const payMethods = document.querySelectorAll('input[name="payment_method"]');
    payMethods.forEach(radio => {
        radio.addEventListener('change', () => updateBreakfastPrice());
    });
    
    // Initialize voucher handlers
    const vouchers = document.querySelectorAll('input[name="breakfast_voucher_id"]');
    vouchers.forEach(radio => {
        radio.addEventListener('change', updateBreakfastPrice);
    });
    
    // Initial calculation
    updateBreakfastPrice();
});


// Booking Confirmation Logic

function calculatePointsEarned(paymentAmount) {
    if (paymentAmount <= 0) return 0;
    // Formula: 1 dollar = 10 base points, then multiply by tier multiplier
    // Points are calculated based on actual payment amount (including breakfast if paid)
    const basePoints = Math.floor(paymentAmount * 10);  // 10 points per $1
    const pointsEarned = Math.floor(basePoints * window.bookingData.multiplier);
    return pointsEarned;
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
        // newTotal already includes breakfast price (or 0 if voucher used)
        pointsEarned = calculatePointsEarned(remainingBalance);
    } else {
        // Paying with cash/card - earn points on full amount (including breakfast if paid)
        // newTotal already includes breakfast price (or 0 if voucher used)
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

function toggleCardOptions() {
    const payByCard = document.getElementById('pay_by_card');
    const cardOptionsContainer = document.getElementById('card_options_container');
    const noCardWarning = document.getElementById('no_card_selected_warning');
    
    if (payByCard && payByCard.checked) {
        if (cardOptionsContainer) {
            cardOptionsContainer.style.display = 'block';
        }
    } else {
        if (cardOptionsContainer) {
            cardOptionsContainer.style.display = 'none';
        }
        // Uncheck all card selection options when Pay by Card is deselected
        const cardSelections = document.querySelectorAll('input[name="card_selection"]');
        cardSelections.forEach(radio => {
            radio.checked = false;
        });
        // Hide warning when switching away from Pay by Card
        if (noCardWarning) noCardWarning.style.display = 'none';
    }
    updatePaymentMethod();
}

function selectCard(cardId) {
    // Find and check the radio button
    const radio = document.getElementById(cardId);
    if (radio) {
        radio.checked = true;
        
        // Remove selected class from all cards
        document.querySelectorAll('.payment-card-option').forEach(card => {
            card.classList.remove('selected');
        });
        
        // Add selected class to clicked card
        const cardOption = radio.closest('.payment-card-option');
        if (cardOption) {
            cardOption.classList.add('selected');
        }
        
        // Update payment method
        updatePaymentMethod();
    }
}

function updatePaymentMethod(newTotal) {
    const payByCard = document.getElementById('pay_by_card');
    const payWithPoints = document.getElementById('pay_with_points');
    const pointsInfo = document.getElementById('points_payment_info');
    const pointsNeededSpan = document.getElementById('points_needed');
    const remainingBalanceSpan = document.getElementById('remaining_balance');
    const noCardWarning = document.getElementById('no_card_selected_warning');
    const insufficientPointsWarning = document.getElementById('insufficient_points_warning');
    const completeBtn = document.getElementById('complete_booking_btn');
    
    // Update card selection visual state
    if (payByCard && payByCard.checked) {
        const selectedCard = document.querySelector('input[name="card_selection"]:checked');
        if (selectedCard) {
            // Remove selected class from all cards
            document.querySelectorAll('.payment-card-option').forEach(card => {
                card.classList.remove('selected');
            });
            
            // Add selected class to checked card
            const cardOption = selectedCard.closest('.payment-card-option');
            if (cardOption) {
                cardOption.classList.add('selected');
            }
        }
    } else {
        // Remove selected class when Pay by Card is not selected
        document.querySelectorAll('.payment-card-option').forEach(card => {
            card.classList.remove('selected');
        });
    }
    
    // Get the actual payment method value
    let actualPaymentMethod = null;
    let isValidPayment = true;
    
    if (payByCard && payByCard.checked) {
        const selectedCard = document.querySelector('input[name="card_selection"]:checked');
        if (selectedCard) {
            actualPaymentMethod = selectedCard.value;
        } else {
            // No card selected
            isValidPayment = false;
            if (noCardWarning) noCardWarning.style.display = 'block';
        }
    } else if (payWithPoints && payWithPoints.checked) {
        actualPaymentMethod = 'points';
        const total = newTotal || window.bookingData.baseTotal + (window.bookingData.breakfastIncluded ? window.bookingData.breakfastPrice : 0);
        const pointsNeeded = Math.ceil(total * window.bookingData.pointsPerDollar);
        
        if (window.bookingData.userPoints < pointsNeeded) {
            // Insufficient points
            isValidPayment = false;
            if (insufficientPointsWarning) insufficientPointsWarning.style.display = 'block';
        }
    } else {
        const payAtHotel = document.getElementById('pay_at_hotel');
        if (payAtHotel && payAtHotel.checked) {
            actualPaymentMethod = 'pay_at_hotel';
        }
    }
    
    // Hide warnings when payment is valid
    if (isValidPayment) {
        if (noCardWarning) noCardWarning.style.display = 'none';
        if (insufficientPointsWarning) insufficientPointsWarning.style.display = 'none';
    }
    
    // Update points payment info
    if (payWithPoints && payWithPoints.checked) {
        if (pointsInfo) pointsInfo.style.display = 'block';
        const total = newTotal || window.bookingData.baseTotal + (window.bookingData.breakfastIncluded ? window.bookingData.breakfastPrice : 0);
        const pointsNeeded = Math.ceil(total * window.bookingData.pointsPerDollar);
        const remainingBalance = Math.max(0, total - (window.bookingData.userPoints / window.bookingData.pointsPerDollar));
        
        if (pointsNeededSpan) pointsNeededSpan.textContent = pointsNeeded.toLocaleString();
        if (remainingBalanceSpan) remainingBalanceSpan.textContent = '$' + remainingBalance.toFixed(2);
    } else {
        if (pointsInfo) pointsInfo.style.display = 'none';
    }
    
    // Enable/disable Complete button
    if (completeBtn) {
        if (isValidPayment) {
            completeBtn.disabled = false;
            completeBtn.style.background = '#1e3a8a';
            completeBtn.style.opacity = '1';
            completeBtn.style.cursor = 'pointer';
        } else {
            completeBtn.disabled = true;
            completeBtn.style.background = '#9ca3af';
            completeBtn.style.opacity = '0.6';
            completeBtn.style.cursor = 'not-allowed';
        }
    }
}

// Initialization on load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize payment method handlers
    const payMethods = document.querySelectorAll('input[name="payment_method"]');
    payMethods.forEach(radio => {
        radio.addEventListener('change', () => {
            updateBreakfastPrice();
            updatePaymentMethod();
        });
    });
    
    // Initialize voucher handlers
    const vouchers = document.querySelectorAll('input[name="breakfast_voucher_id"]');
    vouchers.forEach(radio => {
        radio.addEventListener('change', updateBreakfastPrice);
    });
    
    // Initialize card selection handlers
    const cardSelections = document.querySelectorAll('input[name="card_selection"]');
    cardSelections.forEach(radio => {
        radio.addEventListener('change', () => {
            updatePaymentMethod();
        });
    });
    
    // Initialize card selection visual state
    const selectedCard = document.querySelector('input[name="card_selection"]:checked');
    if (selectedCard) {
        const cardOption = selectedCard.closest('.payment-card-option');
        if (cardOption) {
            cardOption.classList.add('selected');
        }
    }
    
    // Initial calculation
    updateBreakfastPrice();
    updatePaymentMethod();
    
    // Prevent form submission if payment is invalid
    const bookingForm = document.querySelector('form[action*="book_room"]');
    if (bookingForm) {
        bookingForm.addEventListener('submit', function(e) {
            const payByCard = document.getElementById('pay_by_card');
            const payWithPoints = document.getElementById('pay_with_points');
            let isValid = true;
            
            if (payByCard && payByCard.checked) {
                const selectedCard = document.querySelector('input[name="card_selection"]:checked');
                if (!selectedCard) {
                    isValid = false;
                    e.preventDefault();
                    if (document.getElementById('no_card_selected_warning')) {
                        document.getElementById('no_card_selected_warning').style.display = 'block';
                    }
                }
            } else if (payWithPoints && payWithPoints.checked) {
                const total = window.bookingData.baseTotal + (window.bookingData.breakfastIncluded ? window.bookingData.breakfastPrice : 0);
                const pointsNeeded = Math.ceil(total * window.bookingData.pointsPerDollar);
                if (window.bookingData.userPoints < pointsNeeded) {
                    isValid = false;
                    e.preventDefault();
                    if (document.getElementById('insufficient_points_warning')) {
                        document.getElementById('insufficient_points_warning').style.display = 'block';
                    }
                }
            }
            
            return isValid;
        });
    }
});


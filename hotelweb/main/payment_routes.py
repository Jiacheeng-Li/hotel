
@bp.route('/account/payment-method/add', methods=['POST'])
@login_required
def add_card():
    cardholder_name = request.form.get('cardholder_name')
    card_number = request.form.get('card_number')
    expiry_month = request.form.get('expiry_month')
    expiry_year = request.form.get('expiry_year')
    cvv = request.form.get('cvv')
    
    if not all([cardholder_name, card_number, expiry_month, expiry_year, cvv]):
        flash('Please fill in all fields.', 'danger')
        return redirect(url_for('main.account'))
    
    # Simple validation (Mock)
    if len(card_number) < 13:
        flash('Invalid card number.', 'danger')
        return redirect(url_for('main.account'))
        
    # Determine card type (Mock)
    if card_number.startswith('4'):
        card_type = 'Visa'
    elif card_number.startswith('5'):
        card_type = 'Mastercard'
    elif card_number.startswith('3'):
        card_type = 'Amex'
    else:
        card_type = 'Card'
        
    # Check if first card (make default)
    is_default = PaymentMethod.query.filter_by(user_id=current_user.id).count() == 0
    
    card = PaymentMethod(
        user_id=current_user.id,
        card_type=card_type,
        last4=card_number[-4:],
        expiry_month=expiry_month,
        expiry_year=expiry_year,
        cardholder_name=cardholder_name,
        is_default=is_default
    )
    
    db.session.add(card)
    db.session.commit()
    
    flash('Payment method added successfully.', 'success')
    return redirect(url_for('main.account'))

@bp.route('/account/payment-method/delete/<int:card_id>', methods=['POST'])
@login_required
def delete_card(card_id):
    card = PaymentMethod.query.get_or_404(card_id)
    
    if card.user_id != current_user.id:
        abort(403)
        
    db.session.delete(card)
    db.session.commit()
    
    flash('Payment method deleted.', 'success')
    return redirect(url_for('main.account'))

@bp.route('/account/payment-method/default/<int:card_id>', methods=['POST'])
@login_required
def set_default_card(card_id):
    card = PaymentMethod.query.get_or_404(card_id)
    
    if card.user_id != current_user.id:
        abort(403)
        
    # Unset current default
    current_default = PaymentMethod.query.filter_by(user_id=current_user.id, is_default=True).first()
    if current_default:
        current_default.is_default = False
        
    card.is_default = True
    db.session.commit()
    
    flash('Default payment method updated.', 'success')
    return redirect(url_for('main.account'))


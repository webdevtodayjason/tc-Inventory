"""Mobile API Checkout Routes"""
from flask import jsonify, request, current_app
from app.api.mobile import bp, csrf
from app.models.inventory import InventoryItem, ComputerSystem, InventoryTransaction
from app.models.mobile import MobileCheckoutReason
from app.api.mobile.auth import token_required
from app import db
from datetime import datetime
from flask_restx import Resource
from app.api.mobile.swagger import api, ns_checkout, checkout_reason_model, checkout_request_model, history_model

@ns_checkout.route('/reasons')
class CheckoutReasons(Resource):
    @csrf.exempt
    @api.doc('get_checkout_reasons')
    @api.response(200, 'Success', [checkout_reason_model])
    @api.response(500, 'Internal server error')
    @token_required
    def get(self, current_user):
        """Get list of active checkout reasons"""
        try:
            reasons = MobileCheckoutReason.query.filter_by(is_active=True).all()
            return [{
                'id': reason.id,
                'name': reason.name,
                'description': reason.description
            } for reason in reasons]

        except Exception as e:
            current_app.logger.error(f'Error getting checkout reasons: {str(e)}')
            return {'error': 'Internal server error'}, 500

@ns_checkout.route('')
class Checkout(Resource):
    @csrf.exempt
    @api.doc('process_checkout')
    @api.expect(checkout_request_model)
    @api.response(200, 'Checkout processed successfully')
    @api.response(400, 'Validation Error')
    @api.response(404, 'Item/System not found')
    @api.response(500, 'Internal server error')
    @token_required
    def post(self, current_user):
        """Process a checkout transaction"""
        try:
            data = request.get_json()
            if not data:
                return {'error': 'No data provided'}, 400

            # Validate required fields
            required_fields = ['type', 'id', 'reason_id']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return {'error': f'Missing required fields: {", ".join(missing_fields)}'}, 400

            # Get checkout reason
            reason = MobileCheckoutReason.query.get(data['reason_id'])
            if not reason or not reason.is_active:
                return {'error': 'Invalid or inactive checkout reason'}, 400

            # Process based on type
            if data['type'] == 'item':
                item = InventoryItem.query.get(data['id'])
                if not item:
                    return {'error': 'Item not found'}, 404

                # Check quantity
                quantity = data.get('quantity', 1)
                if quantity > item.quantity:
                    return {'error': 'Insufficient quantity available'}, 400

                # Create transaction
                transaction = InventoryTransaction(
                    item_id=item.id,
                    user_id=current_user.id,
                    quantity=quantity,
                    transaction_type='checkout',
                    notes=data.get('notes', ''),
                    checkout_reason=reason.name,
                    is_mobile=True
                )
                item.quantity -= quantity

            elif data['type'] == 'system':
                system = ComputerSystem.query.get(data['id'])
                if not system:
                    return {'error': 'System not found'}, 404

                if system.status != 'available':
                    return {'error': 'System is not available for checkout'}, 400

                # Update system status
                system.status = 'checked_out'
                system.checked_out_by = current_user
                system.checked_out_at = datetime.utcnow()
                system.checkout_reason = reason.name
                system.checkout_notes = data.get('notes', '')

            else:
                return {'error': 'Invalid checkout type'}, 400

            # Save changes
            db.session.commit()

            return {'message': 'Checkout processed successfully'}

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error processing checkout: {str(e)}')
            return {'error': 'Internal server error'}, 500

@ns_checkout.route('/history')
class CheckoutHistory(Resource):
    @csrf.exempt
    @api.doc('get_user_history')
    @api.response(200, 'Success', [history_model])
    @api.response(500, 'Internal server error')
    @token_required
    def get(self, current_user):
        """Get user's checkout history"""
        try:
            # Get item transactions
            transactions = InventoryTransaction.query.filter_by(
                user_id=current_user.id,
                transaction_type='checkout'
            ).order_by(InventoryTransaction.timestamp.desc()).all()

            # Get system checkouts
            systems = ComputerSystem.query.filter_by(
                checked_out_by_id=current_user.id
            ).all()

            # Combine and format history
            history = []

            # Add item transactions
            for trans in transactions:
                history.append({
                    'type': 'item',
                    'date': trans.timestamp.isoformat(),
                    'item_name': trans.item.name if trans.item else 'Unknown Item',
                    'quantity': trans.quantity,
                    'reason': trans.checkout_reason,
                    'notes': trans.notes
                })

            # Add system checkouts
            for system in systems:
                if system.checked_out_at:  # Only include if actually checked out
                    history.append({
                        'type': 'system',
                        'date': system.checked_out_at.isoformat(),
                        'system_name': f"{system.model.manufacturer} {system.model.model_name}" if system.model else 'Unknown System',
                        'reason': system.checkout_reason,
                        'notes': system.checkout_notes
                    })

            # Sort combined history by date
            history.sort(key=lambda x: x['date'], reverse=True)

            return history

        except Exception as e:
            current_app.logger.error(f'Error getting user history: {str(e)}')
            return {'error': 'Internal server error'}, 500 
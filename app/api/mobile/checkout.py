"""Mobile API Checkout Routes"""
from flask import jsonify, request, current_app
from app.api.mobile import bp, csrf, api
from app.models.inventory import InventoryItem, ComputerSystem, Transaction
from app.models.mobile import MobileCheckoutReason
from app.api.mobile.auth import token_required
from app import db
from datetime import datetime
from flask_restx import Resource
from app.api.mobile.swagger import (
    checkout_reason_model, checkout_request_model, history_model,
    item_model, system_model, ns_checkout
)
from app.utils.activity_logger import log_activity
from flask_restx import marshal

# Routes start here
@ns_checkout.route('/reasons')
class CheckoutReasons(Resource):
    @csrf.exempt
    @api.doc('get_checkout_reasons')
    @api.response(200, 'Success', [checkout_reason_model])
    @api.response(500, 'Internal server error')
    @token_required
    def get(self, current_user):
        """Get list of checkout reasons"""
        try:
            reasons = MobileCheckoutReason.query.all()
            return {
                'reasons': [
                    {
                        'id': reason.id,
                        'name': reason.name,
                        'description': reason.description
                    } for reason in reasons
                ]
            }
        except Exception as e:
            current_app.logger.error(f'Error getting checkout reasons: {str(e)}')
            return {'error': 'Internal server error'}, 500

@ns_checkout.route('/search/<string:barcode>')
@api.doc(security='Bearer')
class CheckoutSearch(Resource):
    @csrf.exempt
    @api.doc('search_for_checkout')
    @api.response(200, 'Success', item_model)
    @api.response(404, 'Item not found or not available for checkout')
    @api.response(500, 'Internal server error')
    @token_required
    def get(self, current_user, barcode):
        """Search for an item by barcode for checkout"""
        try:
            # First try to find an item
            item = InventoryItem.query.filter_by(tracking_id=barcode).first()
            if item:
                if item.quantity > 0:
                    return marshal(item, item_model), 200
                else:
                    return {'message': 'Item is out of stock'}, 404

            # If no item found, try to find a system
            system = ComputerSystem.query.filter_by(tracking_id=barcode).first()
            if system:
                if system.status == 'available':
                    return marshal(system, system_model), 200
                else:
                    return {'message': f'System is not available (Status: {system.status})'}, 404

            return {'message': 'Item or system not found'}, 404

        except Exception as e:
            current_app.logger.error(f'Error in checkout search: {str(e)}')
            return {'message': 'Internal server error', 'error': True}, 500

@ns_checkout.route('')
class Checkout(Resource):
    method_decorators = [token_required]  # Apply token_required to all methods
    
    @csrf.exempt
    @api.doc('process_checkout')
    @api.expect(checkout_request_model)
    @api.response(200, 'Checkout processed successfully')
    @api.response(400, 'Validation Error')
    @api.response(404, 'Item/System not found')
    @api.response(500, 'Internal server error')
    def post(self, current_user):
        """Process a checkout transaction"""
        try:
            data = request.get_json()
            current_app.logger.info(f'Processing checkout request: {data}')
            
            if not data:
                return {'error': 'No data provided'}, 400

            # Validate required fields
            required_fields = ['type', 'id', 'reason_id']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return {'error': f'Missing required fields: {", ".join(missing_fields)}'}, 400

            # Get checkout reason
            reason = MobileCheckoutReason.query.get(data['reason_id'])
            if not reason:
                current_app.logger.error(f'Invalid checkout reason ID: {data["reason_id"]}')
                return {'error': 'Invalid checkout reason'}, 400
            
            if not reason.is_active:
                current_app.logger.error(f'Checkout reason {reason.name} is not active')
                return {'error': 'Checkout reason is not active'}, 400

            # Process based on type
            if data['type'] == 'item':
                item = InventoryItem.query.get(data['id'])
                if not item:
                    return {'error': 'Item not found'}, 404

                # Check quantity
                quantity = data.get('quantity', 1)
                if quantity > item.quantity:
                    return {'error': 'Insufficient quantity available'}, 400

                try:
                    # Create transaction
                    transaction = Transaction(
                        item_id=item.id,
                        user_id=current_user.id,
                        quantity=quantity,
                        transaction_type='checkout',
                        notes=data.get('notes', ''),
                        checkout_reason=reason.name,
                        is_mobile=True,
                        timestamp=datetime.utcnow()
                    )
                    
                    # Update item quantity
                    old_quantity = item.quantity
                    item.quantity -= quantity
                    
                    # Add transaction to session
                    db.session.add(transaction)
                    
                    # Log activity for system logs
                    current_app.logger.info(f'[CHECKOUT] Mobile user {current_user.username} checked out {item.name} (x{quantity}) - {reason.name}')
                    log_activity(
                        current_user.id,
                        'mobile_checkout',
                        f'Mobile checkout by {current_user.username}: {item.name} (x{quantity}) - {reason.name}',
                        details={
                            'item_id': item.id,
                            'item_name': item.name,
                            'quantity': quantity,
                            'old_quantity': old_quantity,
                            'new_quantity': item.quantity,
                            'reason': reason.name,
                            'username': current_user.username,
                            'notes': data.get('notes', '')
                        }
                    )

                except Exception as e:
                    current_app.logger.error(f'[CHECKOUT] Failed: {str(e)}')
                    db.session.rollback()
                    return {'error': str(e)}, 500

            elif data['type'] == 'system':
                system = ComputerSystem.query.get(data['id'])
                if not system:
                    return {'error': 'System not found'}, 404

                if system.status != 'available':
                    return {'error': 'System is not available for checkout'}, 400

                try:
                    # Update system status
                    system.status = 'checked_out'
                    system.checked_out_by = current_user
                    system.checked_out_at = datetime.utcnow()
                    system.checkout_reason = reason.name
                    system.checkout_notes = data.get('notes', '')
                    
                    # Log activity for system logs
                    current_app.logger.info(f'[CHECKOUT] Mobile user {current_user.username} checked out system {system.model.manufacturer} {system.model.model_name} - {reason.name}')
                    log_activity(
                        current_user.id,
                        'mobile_checkout',
                        f'Mobile checkout by {current_user.username}: {system.model.manufacturer} {system.model.model_name} - {reason.name}',
                        details={
                            'system_id': system.id,
                            'system_name': f"{system.model.manufacturer} {system.model.model_name}",
                            'reason': reason.name,
                            'username': current_user.username,
                            'notes': data.get('notes', '')
                        }
                    )

                except Exception as e:
                    current_app.logger.error(f'[CHECKOUT] Failed: {str(e)}')
                    db.session.rollback()
                    return {'error': str(e)}, 500

            try:
                # Save changes
                db.session.commit()
                return {'message': 'Checkout processed successfully'}

            except Exception as e:
                current_app.logger.error(f'[CHECKOUT] Database commit failed: {str(e)}')
                db.session.rollback()
                return {'error': str(e)}, 500

        except Exception as e:
            current_app.logger.error(f'[CHECKOUT] Failed: {str(e)}')
            db.session.rollback()
            return {'error': str(e)}, 500

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
            transactions = Transaction.query.filter_by(
                user_id=current_user.id,
                transaction_type='checkout'
            ).order_by(Transaction.timestamp.desc()).all()

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
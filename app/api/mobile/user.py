"""Mobile API User Routes"""
from flask import jsonify, current_app
from flask_restx import Resource, Namespace
from app.api.mobile import api
from app.api.mobile.auth import token_required
from app.models.inventory import InventoryTransaction, ComputerSystem
from datetime import datetime, timedelta

# Create user namespace
ns_user = Namespace('user', description='User operations')

@ns_user.route('/history')
class UserHistory(Resource):
    method_decorators = [token_required]  # Apply token_required to all methods
    
    @api.doc('get_user_history')
    @api.response(200, 'Success')
    @api.response(500, 'Internal server error')
    def get(self, current_user):
        """Get user's checkout history"""
        try:
            # Get transactions from last 30 days
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            
            # Get item transactions
            transactions = InventoryTransaction.query.filter(
                InventoryTransaction.user_id == current_user.id,
                InventoryTransaction.transaction_type == 'checkout',
                InventoryTransaction.timestamp >= thirty_days_ago
            ).order_by(InventoryTransaction.timestamp.desc()).all()

            # Get system checkouts
            systems = ComputerSystem.query.filter(
                ComputerSystem.checked_out_by_id == current_user.id,
                ComputerSystem.checked_out_at >= thirty_days_ago
            ).all()

            # Format history
            history = []

            # Add item transactions
            for trans in transactions:
                history.append({
                    'type': 'item',
                    'date': trans.timestamp.isoformat(),
                    'item_id': trans.item_id,
                    'item_name': trans.item.name if trans.item else 'Unknown Item',
                    'quantity': trans.quantity,
                    'reason': trans.checkout_reason,
                    'notes': trans.notes
                })

            # Add system checkouts
            for system in systems:
                if system.checked_out_at:
                    history.append({
                        'type': 'system',
                        'date': system.checked_out_at.isoformat(),
                        'system_id': system.id,
                        'system_name': f"{system.model.manufacturer} {system.model.model_name}" if system.model else 'Unknown System',
                        'reason': system.checkout_reason,
                        'notes': system.checkout_notes
                    })

            # Sort combined history by date
            history.sort(key=lambda x: x['date'], reverse=True)

            return history

        except Exception as e:
            current_app.logger.error(f'Error getting user history: {str(e)}')
            return {'error': str(e)}, 500 
from flask_restx import Namespace, Resource
from flask import jsonify, current_app
from app.models import InventoryItem
from app.api.mobile.auth import token_required
from app.api.mobile import api

# Create item namespace
ns_item = Namespace('item', description='Item operations')

@ns_item.route('/<string:tracking_id>')
class Item(Resource):
    @ns_item.doc('get_item')
    @ns_item.response(200, 'Success')
    @ns_item.response(404, 'Item not found')
    @token_required
    def get(self, current_user, tracking_id):
        """Get item details by tracking ID"""
        try:
            item = InventoryItem.query.filter_by(tracking_id=tracking_id).first()
            if not item:
                return {'error': 'Item not found'}, 404

            return {
                'id': item.id,
                'name': item.name,
                'tracking_id': item.tracking_id,
                'quantity': item.quantity,
                'category': str(item.category),
                'location': item.location,
                'status': item.status
            }

        except Exception as e:
            current_app.logger.error(f'Error getting item details: {str(e)}')
            return {'error': 'Internal server error'}, 500 
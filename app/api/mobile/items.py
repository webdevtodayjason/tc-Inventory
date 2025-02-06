"""Mobile API Item Routes"""
from flask import jsonify, current_app
from app.api.mobile import bp, csrf
from app.models.inventory import InventoryItem, ComputerSystem
from app.api.mobile.auth import token_required
from flask_restx import Resource
from app.api.mobile.swagger import api, ns_items, ns_systems, item_model, system_model
from flask_restx import marshal

@ns_items.route('/<string:barcode>')
@api.doc(security='Bearer')
class ItemLookup(Resource):
    @csrf.exempt
    @api.doc('get_item')
    @api.response(200, 'Success', item_model)
    @api.response(404, 'Item not found')
    @api.response(500, 'Internal server error')
    @token_required
    def get(self, current_user, barcode):
        """Get item details by barcode"""
        try:
            item = InventoryItem.query.filter_by(tracking_id=barcode).first()
            if not item:
                return {'message': 'Item not found', 'error': True}, 404
            return marshal(item, item_model), 200
        except Exception as e:
            current_app.logger.error(f'Error getting item details: {str(e)}')
            return {'message': 'Internal server error', 'error': True}, 500

@ns_systems.route('/<string:barcode>')
@api.doc(security='Bearer')
class SystemLookup(Resource):
    @csrf.exempt
    @api.doc('get_system')
    @api.response(200, 'Success', system_model)
    @api.response(404, 'System not found')
    @api.response(500, 'Internal server error')
    @token_required
    def get(self, current_user, barcode):
        """Get computer system details by barcode"""
        try:
            system = ComputerSystem.query.filter_by(tracking_id=barcode).first()
            if not system:
                return {'message': 'System not found', 'error': True}, 404
            return marshal(system, system_model), 200
        except Exception as e:
            current_app.logger.error(f'Error getting system details: {str(e)}')
            return {'message': 'Internal server error', 'error': True}, 500 
from flask_restx import Namespace, Resource
from flask import jsonify, current_app
from app.models import ComputerSystem
from app.api.mobile.auth import token_required
from app.api.mobile import api

# Create system namespace
ns_system = Namespace('system', description='System operations')

@ns_system.route('/<string:tracking_id>')
class SystemLookup(Resource):
    @ns_system.doc('get_system')
    @ns_system.response(200, 'Success')
    @ns_system.response(404, 'System not found')
    @token_required
    def get(self, current_user, tracking_id):
        """Get system details by tracking ID"""
        try:
            system = ComputerSystem.query.filter_by(tracking_id=tracking_id).first()
            if not system:
                return {'error': 'System not found'}, 404

            return {
                'id': system.id,
                'name': system.name,
                'tracking_id': system.tracking_id,
                'status': system.status,
                'location': system.location,
                'notes': system.notes
            }

        except Exception as e:
            current_app.logger.error(f'Error getting system details: {str(e)}')
            return {'error': 'Internal server error'}, 500 
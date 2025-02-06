"""Mobile API Search Routes"""
from flask import jsonify, current_app, request
from app.api.mobile import bp, csrf
from app.models.inventory import InventoryItem, ComputerSystem, ComputerModel
from app.api.mobile.auth import token_required
from flask_restx import Resource
from app.api.mobile.swagger import api, ns_search, item_model, system_model, search_results_model
from flask_restx import marshal
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

@ns_search.route('/items/search')
@api.doc(security='Bearer')
class ItemSearch(Resource):
    @csrf.exempt
    @api.doc('search_items')
    @api.param('q', 'Search query (name or tracking ID)')
    @api.param('page', 'Page number (default: 1)')
    @api.param('limit', 'Results per page (default: 20)')
    @api.response(200, 'Success', search_results_model)
    @api.response(400, 'Invalid request')
    @api.response(500, 'Internal server error')
    @token_required
    def get(self, current_user):
        """Search inventory items by name or tracking ID"""
        try:
            # Get query parameters
            query = request.args.get('q', '').strip()
            page = int(request.args.get('page', 1))
            limit = min(int(request.args.get('limit', 20)), 50)  # Cap at 50 items per page

            if not query:
                return {'message': 'Search query is required', 'error': True}, 400

            # Build search query
            search_query = InventoryItem.query.options(
                joinedload(InventoryItem.tags),
                joinedload(InventoryItem.transactions),
                joinedload(InventoryItem.purchase_links),
                joinedload(InventoryItem.creator),
                joinedload(InventoryItem.category)
            ).filter(
                or_(
                    InventoryItem.name.ilike(f'%{query}%'),
                    InventoryItem.tracking_id.ilike(f'%{query}%'),
                    InventoryItem.manufacturer.ilike(f'%{query}%'),
                    InventoryItem.mpn.ilike(f'%{query}%')
                )
            )

            # Execute paginated query
            paginated_results = search_query.paginate(page=page, per_page=limit)
            
            # Marshal the results
            results = [marshal(item, item_model) for item in paginated_results.items]
            
            response = {
                'results': results,
                'total': paginated_results.total,
                'pages': paginated_results.pages,
                'current_page': page,
                'has_next': paginated_results.has_next,
                'has_prev': paginated_results.has_prev
            }
            
            return marshal(response, search_results_model), 200

        except ValueError as e:
            return {'message': 'Invalid page or limit parameter', 'error': True}, 400
        except Exception as e:
            current_app.logger.error(f'Error searching items: {str(e)}')
            return {'message': 'Internal server error', 'error': True}, 500

@ns_search.route('/systems/search')
@api.doc(security='Bearer')
class SystemSearch(Resource):
    @csrf.exempt
    @api.doc('search_systems')
    @api.param('q', 'Search query (tracking ID or model info)')
    @api.param('page', 'Page number (default: 1)')
    @api.param('limit', 'Results per page (default: 20)')
    @api.response(200, 'Success', search_results_model)
    @api.response(400, 'Invalid request')
    @api.response(500, 'Internal server error')
    @token_required
    def get(self, current_user):
        """Search computer systems by tracking ID or model info"""
        try:
            # Get query parameters
            query = request.args.get('q', '').strip()
            page = int(request.args.get('page', 1))
            limit = min(int(request.args.get('limit', 20)), 50)  # Cap at 50 items per page

            if not query:
                return {'message': 'Search query is required', 'error': True}, 400

            # Build search query with joins
            search_query = ComputerSystem.query.join(
                ComputerModel,
                ComputerSystem.model_id == ComputerModel.id
            ).filter(
                or_(
                    ComputerSystem.tracking_id.ilike(f'%{query}%'),
                    ComputerModel.manufacturer.ilike(f'%{query}%'),
                    ComputerModel.model_name.ilike(f'%{query}%')
                )
            )

            # Execute paginated query
            paginated_results = search_query.paginate(page=page, per_page=limit)
            
            # Marshal the results
            results = [marshal(system, system_model) for system in paginated_results.items]
            
            response = {
                'results': results,
                'total': paginated_results.total,
                'pages': paginated_results.pages,
                'current_page': page,
                'has_next': paginated_results.has_next,
                'has_prev': paginated_results.has_prev
            }
            
            return marshal(response, search_results_model), 200

        except ValueError as e:
            return {'message': 'Invalid page or limit parameter', 'error': True}, 400
        except Exception as e:
            current_app.logger.error(f'Error searching systems: {str(e)}')
            return {'message': 'Internal server error', 'error': True}, 500 
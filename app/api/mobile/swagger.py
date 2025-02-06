"""Swagger configuration for mobile API"""
from flask_restx import Api, Namespace, fields

# Create API with prefix handling
api = Api(
    title='TC Inventory Mobile API',
    version='1.0',
    description='API for TC Inventory mobile app',
    doc='/docs',
    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Add "Bearer " prefix to your JWT token'
        }
    },
    security='Bearer'  # Apply Bearer auth by default to all endpoints
)

# Create namespaces
ns_auth = Namespace('auth', description='Authentication operations')
ns_items = Namespace('items', description='Item operations')
ns_systems = Namespace('systems', description='System operations')
ns_search = Namespace('search', description='Search operations')
ns_checkout = Namespace('checkout', description='Checkout operations')

# Add namespaces to API
api.add_namespace(ns_auth)
api.add_namespace(ns_items)
api.add_namespace(ns_systems)
api.add_namespace(ns_search)
api.add_namespace(ns_checkout)

# Models
tag_model = api.model('Tag', {
    'id': fields.Integer,
    'name': fields.String,
    'color': fields.String
})

computer_model_model = api.model('ComputerModel', {
    'id': fields.Integer,
    'manufacturer': fields.String,
    'model_name': fields.String,
    'type': fields.String
})

cpu_model = api.model('CPU', {
    'id': fields.Integer,
    'manufacturer': fields.String,
    'model': fields.String,
    'speed': fields.String
})

history_model = api.model('CheckoutHistory', {
    'type': fields.String(description='Transaction type (item/system)'),
    'date': fields.String(description='Checkout date'),
    'item_name': fields.String(description='Item name (for items)'),
    'system_name': fields.String(description='System name (for systems)'),
    'quantity': fields.Integer(description='Quantity (for items)'),
    'reason': fields.String(description='Checkout reason'),
    'notes': fields.String(description='Notes')
})

purchase_link_model = api.model('PurchaseLink', {
    'id': fields.Integer,
    'url': fields.String,
    'title': fields.String,
    'created_at': fields.String
})

item_model = api.model('Item', {
    'id': fields.Integer,
    'tracking_id': fields.String,
    'name': fields.String,
    'description': fields.String,
    'quantity': fields.Integer,
    'min_quantity': fields.Integer,
    'reorder_threshold': fields.Integer,
    'location': fields.String,
    'storage_location': fields.String,
    'manufacturer': fields.String,
    'mpn': fields.String,
    'image_url': fields.String,
    'cost': fields.Float,
    'sell_price': fields.Float,
    'purchase_url': fields.String,
    'created_at': fields.String,
    'updated_at': fields.String,
    'category_id': fields.Integer,
    'status': fields.String,
    'creator_id': fields.Integer,
    'creator': fields.Nested(api.model('ItemCreator', {
        'id': fields.Integer,
        'username': fields.String
    })),
    'category': fields.Nested(api.model('ItemCategory', {
        'id': fields.Integer,
        'name': fields.String
    })),
    'tags': fields.List(fields.Nested(tag_model)),
    'transactions': fields.List(fields.Nested(history_model)),
    'purchase_links': fields.List(fields.Nested(purchase_link_model))
})

system_model = api.model('System', {
    'id': fields.Integer,
    'tracking_id': fields.String,
    'model': fields.Nested(computer_model_model),
    'serial_number': fields.String,
    'status': fields.String,
    'location': fields.String,
    'notes': fields.String,
    'cpu': fields.Nested(cpu_model),
    'ram': fields.String,
    'storage': fields.String,
    'os': fields.String,
    'tags': fields.List(fields.Nested(tag_model))
})

# Response models
search_results_model = api.model('SearchResults', {
    'results': fields.Raw(description='List of search results (items or systems)'),
    'total': fields.Integer(description='Total number of results'),
    'pages': fields.Integer(description='Total number of pages'),
    'current_page': fields.Integer(description='Current page number'),
    'has_next': fields.Boolean(description='Whether there is a next page'),
    'has_prev': fields.Boolean(description='Whether there is a previous page')
})

# Auth models
login_model = api.model('Login', {
    'username': fields.String(required=True, description='Username'),
    'pin': fields.String(required=True, description='PIN code')
})

user_model = api.model('User', {
    'id': fields.Integer(description='User ID'),
    'username': fields.String(description='Username'),
    'role': fields.String(description='User role')
})

token_response = api.model('TokenResponse', {
    'token': fields.String(description='JWT token'),
    'user': fields.Nested(user_model)
})

checkout_reason_model = api.model('CheckoutReason', {
    'id': fields.Integer(description='Reason ID'),
    'name': fields.String(description='Reason name'),
    'description': fields.String(description='Reason description')
})

checkout_request_model = api.model('CheckoutRequest', {
    'type': fields.String(required=True, description='Type of checkout (item/system)'),
    'id': fields.Integer(required=True, description='Item/System ID'),
    'reason_id': fields.Integer(required=True, description='Checkout reason ID'),
    'quantity': fields.Integer(description='Quantity to checkout (for items)'),
    'notes': fields.String(description='Checkout notes')
}) 
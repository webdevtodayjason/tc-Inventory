"""Swagger documentation for the mobile API"""
from flask_restx import Api, Resource, fields
from app.api.mobile import bp

# Create API instance
authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Enter your JWT token with the Bearer prefix'
    }
}

api = Api(
    bp,
    version='1.0',
    title='TC Inventory Mobile API',
    description='API documentation for TC Inventory mobile application',
    doc='/docs',
    authorizations=authorizations,
    security=[{'Bearer': []}]  # Apply security globally
)

# Define namespaces
ns_auth = api.namespace('auth', description='Authentication operations')
ns_items = api.namespace('item', description='Item operations')
ns_systems = api.namespace('system', description='System operations')
ns_checkout = api.namespace('checkout', description='Checkout operations')

# Define models
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

item_model = api.model('Item', {
    'id': fields.Integer(description='Item ID'),
    'name': fields.String(description='Item name'),
    'tracking_id': fields.String(description='Tracking ID'),
    'quantity': fields.Integer(description='Available quantity'),
    'category': fields.String(description='Item category'),
    'location': fields.String(description='Item location'),
    'status': fields.String(description='Item status'),
    'notes': fields.String(description='Item notes')
})

# Updated system model with nested structures
computer_model = api.model('ComputerModel', {
    'manufacturer': fields.String(description='Model manufacturer'),
    'model_name': fields.String(description='Model name'),
    'model_type': fields.String(description='Model type')
})

cpu_model = api.model('CPU', {
    'manufacturer': fields.String(description='CPU manufacturer'),
    'model': fields.String(description='CPU model'),
    'speed': fields.Float(description='CPU speed in GHz'),
    'cores': fields.Integer(description='Number of cores')
})

system_model = api.model('System', {
    'id': fields.Integer(description='System ID'),
    'tracking_id': fields.String(description='Tracking ID'),
    'model': fields.Nested(computer_model, description='Computer model details'),
    'serial_number': fields.String(description='Serial number'),
    'status': fields.String(description='System status'),
    'location': fields.String(description='System location'),
    'notes': fields.String(description='System notes'),
    'cpu': fields.Nested(cpu_model, description='CPU details')
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

history_model = api.model('CheckoutHistory', {
    'type': fields.String(description='Transaction type (item/system)'),
    'date': fields.String(description='Checkout date'),
    'item_name': fields.String(description='Item name (for items)'),
    'system_name': fields.String(description='System name (for systems)'),
    'quantity': fields.Integer(description='Quantity (for items)'),
    'reason': fields.String(description='Checkout reason'),
    'notes': fields.String(description='Notes')
})

# Import route handlers after defining models to avoid circular imports
from app.api.mobile import auth, items, checkout 
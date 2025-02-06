"""Swagger configuration for mobile API"""
from flask_restx import Api, Namespace, fields

# Create API with prefix handling
api = Api(
    title='TC Inventory Mobile API',
    version='1.0',
    description="""
# TC Inventory Mobile API Documentation

This API provides mobile access to the TC Inventory System. It enables inventory management, barcode scanning, 
and checkout functionality through mobile devices.

## Quick Links
- [API Reference](../mobile/swagger)
- [Code Examples](../docs/examples)
- [Postman Collection](../docs/postman)
- [Mobile App Source](https://github.com/webdevtodayjason/tc-Inventory/tree/main/tc_inventory_mobile)

## Authentication

All endpoints require JWT authentication. To authenticate:
1. Call the `/auth/login` endpoint with username and PIN
2. Use the returned token in subsequent requests in the Authorization header:
   ```
   Authorization: Bearer <your_token>
   ```

## Rate Limiting
- 100 requests per minute per IP
- 1000 requests per hour per user

## Common Response Codes
- 200: Success
- 400: Bad Request - Check request parameters
- 401: Unauthorized - Invalid or missing token
- 403: Forbidden - Insufficient permissions
- 404: Not Found - Resource doesn't exist
- 429: Too Many Requests - Rate limit exceeded
- 500: Server Error - Please report to support

## Development Environment
- Local API: /api/mobile
- Local API Docs: ../docs
- Local Swagger UI: ../mobile/swagger

## Mobile App Features
- Barcode scanning with Code128 support
- Real-time inventory search
- Quick checkout process
- Dark mode support
- Offline capability
- Push notifications

## Testing Tools
- [Postman Collection](../docs/postman) - Ready-to-use API collection with environment configurations
- [OpenAPI Spec](../docs/openapi) - OpenAPI/Swagger specification file

For detailed implementation examples, see our [Mobile Development Guide](../docs/mobile).
    """,
    doc='/swagger',  # This sets the Swagger UI endpoint to /api/mobile/swagger
    prefix='/api/mobile',  # This ensures all API routes have the correct prefix
    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Add "Bearer " prefix to your JWT token'
        }
    },
    security='Bearer',  # Apply Bearer auth by default to all endpoints
    default_mediatype='application/json',
    validate=True,
    ordered=True
)

# Create namespaces with detailed descriptions
ns_auth = Namespace('auth', 
    description='Authentication operations',
    path='/auth',
    decorators=[],
    validate=True,
    doc={
        'description': """
Authentication endpoints for mobile access.

## Login Process
1. User enters username and PIN
2. System validates credentials
3. Returns JWT token valid for 7 days
4. Token refresh available before expiration

## Security Notes
- PINs must be 4-6 digits
- Failed attempts are rate limited
- Tokens are invalidated on password change
        """
    }
)

ns_items = Namespace('items', 
    description='Item operations',
    path='/items',
    decorators=[],
    validate=True,
    doc={
        'description': """
Item management endpoints for inventory items.

## Item States
- Available: Ready for checkout
- Reserved: Temporarily held
- Checked Out: Currently in use
- Maintenance: Under repair
- Retired: No longer in service

## Barcode Format
Items use Code128 barcodes with format:
```
TC-XXXXXXXX
```
Where X is alphanumeric
        """
    }
)

ns_systems = Namespace('systems', 
    description='System operations',
    path='/systems',
    decorators=[],
    validate=True,
    doc={
        'description': """
Computer system management endpoints.

## System Types
- Desktop
- Laptop
- Server
- Other

## Testing Process
1. Initial intake
2. Hardware verification
3. Performance testing
4. Software setup
5. Final validation
        """
    }
)

ns_search = Namespace('search', 
    description='Search operations',
    path='/search',
    decorators=[],
    validate=True,
    doc={
        'description': """
Search endpoints for finding items and systems.

## Search Features
- Full text search
- Barcode lookup
- Filter by category
- Sort by various fields
- Pagination support

## Search Tips
- Use * for wildcard
- Quotes for exact phrases
- -term to exclude
- category: for filtering
        """
    }
)

ns_checkout = Namespace('checkout', 
    description='Checkout operations',
    path='/checkout',
    decorators=[],
    validate=True,
    doc={
        'description': """
Checkout process endpoints for items and systems.

## Checkout Process
1. Scan item/system
2. Select reason
3. Add notes (optional)
4. Confirm checkout
5. Receive confirmation

## Return Process
1. Scan item/system
2. Verify condition
3. Add notes (optional)
4. Confirm return
        """
    }
)

# Add namespaces to API
api.add_namespace(ns_auth)
api.add_namespace(ns_items)
api.add_namespace(ns_systems)
api.add_namespace(ns_search)
api.add_namespace(ns_checkout)

# Models with detailed documentation
tag_model = api.model('Tag', {
    'id': fields.Integer(description='Unique identifier for the tag', example=1),
    'name': fields.String(description='Tag name (max 50 chars)', max_length=50, example='Testing'),
    'color': fields.String(description='Hex color code (e.g. #FF0000)', pattern='^#[0-9A-Fa-f]{6}$', example='#FF0000')
})

computer_model_model = api.model('ComputerModel', {
    'id': fields.Integer(description='Unique identifier for the model', example=1),
    'manufacturer': fields.String(description='Manufacturer name (e.g. Dell, HP)', example='Dell'),
    'model_name': fields.String(description='Model name/number', example='Optiplex 7090'),
    'type': fields.String(description='System type (desktop/laptop/server/other)', example='desktop')
})

cpu_model = api.model('CPU', {
    'id': fields.Integer(description='Unique identifier for the CPU', example=1),
    'manufacturer': fields.String(description='CPU manufacturer (e.g. Intel, AMD)', example='Intel'),
    'model': fields.String(description='CPU model name', example='Core i7-11700'),
    'speed': fields.String(description='Clock speed in GHz', example='2.5'),
    'benchmark': fields.Integer(description='PassMark score (if available)', example=24356)
})

history_model = api.model('CheckoutHistory', {
    'type': fields.String(description='Transaction type (item/system)'),
    'date': fields.String(description='ISO 8601 formatted date'),
    'item_name': fields.String(description='Item name (for items)'),
    'system_name': fields.String(description='System name (for systems)'),
    'quantity': fields.Integer(description='Quantity checked out (for items)'),
    'reason': fields.String(description='Checkout reason'),
    'notes': fields.String(description='Additional notes')
})

purchase_link_model = api.model('PurchaseLink', {
    'id': fields.Integer(description='Unique identifier for the link'),
    'url': fields.String(description='Purchase URL'),
    'title': fields.String(description='Link title/description'),
    'created_at': fields.String(description='ISO 8601 formatted creation date')
})

# Response models with examples
item_model = api.model('Item', {
    'id': fields.Integer(example=1),
    'tracking_id': fields.String(example='TC-B95F49A3'),
    'name': fields.String(example='USB Network Adapter'),
    'description': fields.String(example='Gigabit USB 3.0 to RJ45 adapter'),
    'quantity': fields.Integer(example=5),
    'min_quantity': fields.Integer(example=2),
    'reorder_threshold': fields.Integer(example=3),
    'location': fields.String(example='Shelf A3'),
    'storage_location': fields.String(example='Warehouse 1'),
    'manufacturer': fields.String(example='TP-Link'),
    'mpn': fields.String(example='UE300'),
    'image_url': fields.String(example='https://inventory.ticom.pro/images/items/UE300.jpg'),
    'cost': fields.Float(example=19.99),
    'sell_price': fields.Float(example=29.99),
    'purchase_url': fields.String(example='https://www.amazon.com/dp/B00YUU3KC6'),
    'created_at': fields.String(example='2024-02-06T12:00:00Z'),
    'updated_at': fields.String(example='2024-02-06T14:30:00Z'),
    'category_id': fields.Integer(example=5),
    'status': fields.String(example='available'),
    'creator_id': fields.Integer(example=1),
    'creator': fields.Nested(api.model('ItemCreator', {
        'id': fields.Integer(example=1),
        'username': fields.String(example='jsmith')
    })),
    'category': fields.Nested(api.model('ItemCategory', {
        'id': fields.Integer(example=5),
        'name': fields.String(example='Network Adapters')
    })),
    'tags': fields.List(fields.Nested(tag_model)),
    'transactions': fields.List(fields.Nested(history_model)),
    'purchase_links': fields.List(fields.Nested(purchase_link_model))
})

system_model = api.model('System', {
    'id': fields.Integer(example=1),
    'tracking_id': fields.String(example='TC-3C7B2D9A'),
    'model': fields.Nested(computer_model_model),
    'serial_number': fields.String(example='SN123456789'),
    'status': fields.String(example='available'),
    'location': fields.String(example='Lab 2'),
    'notes': fields.String(example='Fresh Windows install, ready for use'),
    'cpu': fields.Nested(cpu_model),
    'ram': fields.String(example='32GB'),
    'storage': fields.String(example='1TB NVMe SSD'),
    'os': fields.String(example='Windows 11 Pro'),
    'tags': fields.List(fields.Nested(tag_model))
})

# Search results model with pagination
search_results_model = api.model('SearchResults', {
    'results': fields.Raw(description='List of search results (items or systems)'),
    'total': fields.Integer(description='Total number of results', example=42),
    'pages': fields.Integer(description='Total number of pages', example=3),
    'current_page': fields.Integer(description='Current page number', example=1),
    'has_next': fields.Boolean(description='Whether there is a next page', example=True),
    'has_prev': fields.Boolean(description='Whether there is a previous page', example=False)
})

# Auth models with examples
login_model = api.model('Login', {
    'username': fields.String(required=True, description='Username', example='jsmith'),
    'pin': fields.String(required=True, description='PIN code', example='123456')
})

user_model = api.model('User', {
    'id': fields.Integer(description='User ID', example=1),
    'username': fields.String(description='Username', example='jsmith'),
    'role': fields.String(description='User role', example='technician')
})

token_response = api.model('TokenResponse', {
    'token': fields.String(description='JWT token', example='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'),
    'user': fields.Nested(user_model)
})

checkout_reason_model = api.model('CheckoutReason', {
    'id': fields.Integer(description='Reason ID', example=1),
    'name': fields.String(description='Reason name', example='CLIENT INSTALL'),
    'description': fields.String(description='Reason description', example='Installation at client site')
})

checkout_request_model = api.model('CheckoutRequest', {
    'type': fields.String(required=True, description='Type of checkout (item/system)', example='item'),
    'id': fields.Integer(required=True, description='Item/System ID', example=1),
    'reason_id': fields.Integer(required=True, description='Checkout reason ID', example=1),
    'quantity': fields.Integer(description='Quantity to checkout (for items)', example=1),
    'notes': fields.String(description='Checkout notes', example='Needed for Client ABC setup')
}) 
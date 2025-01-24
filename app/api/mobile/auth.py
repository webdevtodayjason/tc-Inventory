"""Mobile API Authentication Routes"""
from flask import jsonify, request, current_app
from app.api.mobile import bp, csrf
from app.models.user import User
from app.models.mobile import MobileDeviceToken
from app import db
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask_restx import Resource
from app.api.mobile.swagger import api, ns_auth, login_model, token_response

def generate_token(user):
    """Generate JWT token for user"""
    token = jwt.encode({
        'user_id': user.id,
        'username': user.username,
        'exp': datetime.utcnow() + timedelta(days=1)
    }, current_app.config['SECRET_KEY'])
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return {'message': 'Token is missing', 'error': True}, 401
            
        # Check if auth header starts with "Bearer "
        if not auth_header.startswith('Bearer '):
            return {'message': 'Invalid token format - must start with Bearer', 'error': True}, 401
            
        try:
            # Extract token after "Bearer "
            token = auth_header[7:]  # Skip "Bearer "
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return {'message': 'User not found', 'error': True}, 401
            return f(current_user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return {'message': 'Token has expired', 'error': True}, 401
        except jwt.InvalidTokenError:
            return {'message': 'Invalid token', 'error': True}, 401
        except Exception as e:
            current_app.logger.error(f'Token validation error: {str(e)}')
            return {'message': 'Token validation failed', 'error': True}, 401
            
    return decorated

@ns_auth.route('/login')
class Login(Resource):
    @csrf.exempt
    @api.doc('login')
    @api.expect(login_model)
    @api.response(200, 'Success', token_response)
    @api.response(400, 'Validation Error')
    @api.response(401, 'Authentication Failed')
    def post(self):
        """Login with username and PIN"""
        try:
            data = request.get_json()
            if not data:
                return {'error': 'No data provided'}, 400

            username = data.get('username')
            pin = data.get('pin')

            if not username or not pin:
                return {'error': 'Username and PIN are required'}, 400

            user = User.query.filter_by(username=username).first()
            if not user or not user.check_pin(pin):
                return {'error': 'Invalid username or PIN'}, 401

            token = generate_token(user)
            return {
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'role': user.role
                }
            }

        except Exception as e:
            current_app.logger.error(f'Login error: {str(e)}')
            return {'error': 'Internal server error'}, 500

@ns_auth.route('/refresh')
class TokenRefresh(Resource):
    @csrf.exempt
    @api.doc('refresh_token')
    @api.response(200, 'Success', token_response)
    @api.response(401, 'Invalid Token')
    @token_required
    def post(self, current_user):
        """Refresh JWT token"""
        token = generate_token(current_user)
        return {'token': token}, 200

@ns_auth.route('/verify')
class TokenVerify(Resource):
    @csrf.exempt
    @api.doc('verify_token')
    @api.response(200, 'Token is valid')
    @api.response(401, 'Invalid Token')
    @token_required
    def post(self, current_user):
        """Verify JWT token"""
        return {
            'valid': True,
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'role': current_user.role
            }
        }, 200 
"""Mobile API Authentication Routes"""
from flask import jsonify, request, current_app
from app.api.mobile import bp, csrf, api
from app.models.user import User
from app.models.mobile import MobileDeviceToken
from app import db
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask_restx import Resource
from app.api.mobile.swagger import ns_auth, login_model, token_response, user_model

def generate_token(user):
    """Generate JWT token for user"""
    token = jwt.encode({
        'user_id': user.id,
        'username': user.username,
        'exp': datetime.utcnow() + timedelta(days=7)  # Extended to 7 days
    }, current_app.config['SECRET_KEY'])
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return {'message': 'Invalid token format'}, 401

        if not token:
            return {'message': 'Token is missing'}, 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return {'message': 'Invalid token'}, 401
            return f(current_user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return {'message': 'Token has expired'}, 401
        except jwt.InvalidTokenError:
            return {'message': 'Invalid token'}, 401
            
    return decorated

@ns_auth.route('/login')
class Login(Resource):
    @csrf.exempt
    @api.doc('login', security=None)  # No security required for login
    @api.expect(login_model)
    @api.response(200, 'Success', token_response)
    @api.response(400, 'Validation Error')
    @api.response(401, 'Authentication Failed')
    def post(self):
        """
        User login endpoint
        
        Returns a JWT token for use in subsequent API calls.
        Add the token to the Authorization header as: Bearer <token>
        """
        try:
            # Log request details for debugging
            current_app.logger.info(f"[Mobile Login] Received login request")
            current_app.logger.debug(f"[Mobile Login] Headers: {dict(request.headers)}")
            current_app.logger.debug(f"[Mobile Login] Body: {request.get_data(as_text=True)}")
            
            data = request.get_json()
            if not data:
                current_app.logger.error("[Mobile Login] No JSON data received")
                return {'message': 'No data provided'}, 400

            username = data.get('username')
            pin = data.get('pin')

            current_app.logger.info(f"[Mobile Login] Attempting login for user: {username}")

            if not username or not pin:
                current_app.logger.error("[Mobile Login] Missing username or PIN")
                return {'message': 'Missing username or PIN'}, 400

            user = User.query.filter_by(username=username).first()

            if user and user.check_pin(pin):
                token = jwt.encode({
                    'user_id': user.id,
                    'exp': datetime.utcnow() + timedelta(days=7)
                }, current_app.config['SECRET_KEY'])

                current_app.logger.info(f"[Mobile Login] Successful login for user: {username}")
                return {
                    'token': token,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'role': user.role
                    }
                }, 200
            else:
                current_app.logger.warning(f"[Mobile Login] Failed login attempt for user: {username}")
                return {'message': 'Invalid credentials'}, 401

        except Exception as e:
            current_app.logger.error(f"[Mobile Login] Error during login: {str(e)}")
            return {'message': 'Internal server error'}, 500

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
class VerifyToken(Resource):
    @token_required
    def get(self, current_user):
        """Verify token and return user info"""
        return {
            'valid': True,
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'role': current_user.role
            }
        }, 200 
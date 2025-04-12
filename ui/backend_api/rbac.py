import functools
import re
import time
import jwt
from flask import request, jsonify, current_app
import logging
from datetime import datetime, timedelta

# Setup logging
logger = logging.getLogger(__name__)

# Define user roles and permissions
ROLES = {
    'admin': {
        'description': 'Administrator with full access',
        'permissions': ['read:logs', 'read:alerts', 'read:stats', 'write:alerts', 'manage:users', 'manage:system']
    },
    'analyst': {
        'description': 'Security analyst with investigation capabilities',
        'permissions': ['read:logs', 'read:alerts', 'read:stats', 'write:alerts']
    },
    'viewer': {
        'description': 'Read-only user',
        'permissions': ['read:logs', 'read:alerts', 'read:stats']
    }
}

# Role-based access mappings (simplified)
ENDPOINT_PERMISSIONS = {
    'get_logs': 'read:logs',
    'get_alerts': 'read:alerts',
    'get_stats': 'read:stats',
    'update_alert': 'write:alerts',
    'create_user': 'manage:users',
    'update_user': 'manage:users',
    'delete_user': 'manage:users',
    'system_config': 'manage:system'
}

class AuthError(Exception):
    """Exception raised for authentication and authorization errors."""
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

def get_token_from_request():
    """Extract bearer token from Authorization header."""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        raise AuthError({'code': 'invalid_header', 'description': 'Authorization header must start with Bearer'}, 401)
    
    token = auth_header.split(' ')[1]
    if not token:
        raise AuthError({'code': 'invalid_header', 'description': 'Token not found'}, 401)
    
    return token

def validate_jwt(token):
    """Validate JWT token and return payload."""
    try:
        # Get the secret key from Flask app config
        secret_key = current_app.config.get('JWT_SECRET_KEY')
        if not secret_key:
            logger.error("JWT_SECRET_KEY not configured in application")
            raise AuthError({'code': 'invalid_config', 'description': 'JWT configuration error'}, 500)
        
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        # Check if token is expired
        if 'exp' in payload and payload['exp'] < time.time():
            raise AuthError({'code': 'token_expired', 'description': 'Token has expired'}, 401)
            
        return payload
        
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise AuthError({'code': 'invalid_token', 'description': f'Invalid token: {str(e)}'}, 401)

def has_required_permissions(user_permissions, required_permission):
    """Check if user has the required permission."""
    if not required_permission:
        return True
    return required_permission in user_permissions

def auth_required(permission=None):
    """Decorator for routes that require authentication and specific permissions."""
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            try:
                # Get and validate token
                token = get_token_from_request()
                payload = validate_jwt(token)
                
                # Extract user info from payload
                user_id = payload.get('sub') or payload.get('user_id')
                role = payload.get('role', 'viewer')  # Default to viewer if no role
                permissions = ROLES.get(role, {}).get('permissions', [])
                
                # Set current user context
                request.current_user = {
                    'user_id': user_id,
                    'role': role,
                    'permissions': permissions
                }
                
                # Check permissions if specified
                if permission and not has_required_permissions(permissions, permission):
                    logger.warning(f"Access denied: User {user_id} with role {role} lacks permission {permission}")
                    return jsonify({
                        'error': 'forbidden',
                        'message': f'Requires permission: {permission}'
                    }), 403
                
                # Log successful authorization
                logger.debug(f"User {user_id} with role {role} authorized for {request.endpoint}")
                
                # Execute the wrapped function
                return f(*args, **kwargs)
                
            except AuthError as e:
                return jsonify(e.error), e.status_code
                
        return wrapper
    return decorator

def get_permission_for_endpoint(endpoint):
    """Get required permission for an endpoint."""
    return ENDPOINT_PERMISSIONS.get(endpoint)

def admin_required(f):
    """Decorator for routes that require admin role."""
    return auth_required('manage:system')(f)

def generate_token(user_id, role='viewer', expiry_hours=24):
    """Generate a JWT token for a user."""
    secret_key = current_app.config.get('JWT_SECRET_KEY')
    if not secret_key:
        raise ValueError("JWT_SECRET_KEY not configured")
    
    payload = {
        'sub': user_id,
        'role': role,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=expiry_hours)
    }
    
    return jwt.encode(payload, secret_key, algorithm='HS256')

# For testing only - to be removed in production
def get_test_token(role='admin'):
    """Generate a test token for development purposes."""
    if current_app.config.get('ENV') != 'development':
        logger.warning("Attempted to get test token in non-development environment")
        return None
        
    return generate_token('test-user', role)

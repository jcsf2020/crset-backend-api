#!/usr/bin/env python3
"""
CRSET Solutions - Authentication Routes
JWT-based authentication for admin access
"""

import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from functools import wraps
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
auth_bp = Blueprint('auth', __name__)

# JWT Configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'crset-jwt-secret-2025')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Mock admin users (in production, use database)
ADMIN_USERS = {
    'jcsf2020@gmail.com': {
        'password_hash': bcrypt.hashpw('-Portugal2025'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        'role': 'admin',
        'name': 'João Fonseca'
    },
    'admin@crsetsolutions.com': {
        'password_hash': bcrypt.hashpw('-Crsetsolutions2025'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        'role': 'admin',
        'name': 'CRSET Admin'
    }
}

def generate_token(user_email, role='admin'):
    """Generate JWT token for user"""
    payload = {
        'email': user_email,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def verify_token(token):
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid authorization header format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        # Verify token
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        # Add user info to request
        request.current_user = payload
        return f(*args, **kwargs)
    
    return decorated_function

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """Admin login endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400
        
        # Check if user exists
        if email not in ADMIN_USERS:
            logger.warning(f"Login attempt with invalid email: {email}")
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401
        
        user = ADMIN_USERS[email]
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            logger.warning(f"Login attempt with invalid password for: {email}")
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401
        
        # Generate token
        token = generate_token(email, user['role'])
        
        logger.info(f"Successful login for: {email}")
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': {
                'email': email,
                'name': user['name'],
                'role': user['role']
            },
            'expires_in': JWT_EXPIRATION_HOURS * 3600  # seconds
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    """Admin registration endpoint (restricted)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        admin_key = data.get('admin_key', '')
        
        # Validate required fields
        if not all([email, password, name, admin_key]):
            return jsonify({
                'success': False,
                'message': 'Email, password, name and admin_key are required'
            }), 400
        
        # Verify admin key (security measure)
        if admin_key != os.getenv('ADMIN_REGISTRATION_KEY', 'crset-admin-key-2025'):
            logger.warning(f"Registration attempt with invalid admin key from: {email}")
            return jsonify({
                'success': False,
                'message': 'Invalid admin key'
            }), 403
        
        # Check if user already exists
        if email in ADMIN_USERS:
            return jsonify({
                'success': False,
                'message': 'User already exists'
            }), 409
        
        # Validate password strength
        if len(password) < 8:
            return jsonify({
                'success': False,
                'message': 'Password must be at least 8 characters long'
            }), 400
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Add user (in production, save to database)
        ADMIN_USERS[email] = {
            'password_hash': password_hash,
            'role': 'admin',
            'name': name
        }
        
        logger.info(f"New admin user registered: {email}")
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': {
                'email': email,
                'name': name,
                'role': 'admin'
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@auth_bp.route('/auth/verify', methods=['GET'])
@require_auth
def verify():
    """Verify token endpoint"""
    try:
        user_info = request.current_user
        
        return jsonify({
            'success': True,
            'message': 'Token is valid',
            'user': {
                'email': user_info['email'],
                'role': user_info['role']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@auth_bp.route('/auth/logout', methods=['POST'])
@require_auth
def logout():
    """Logout endpoint (client-side token removal)"""
    try:
        user_info = request.current_user
        logger.info(f"User logged out: {user_info['email']}")
        
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        }), 200
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


#!/usr/bin/env python3
"""
CRSET Solutions - Admin Routes
Protected admin endpoints for dashboard management
"""

import os
import json
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from .auth import require_auth
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
admin_bp = Blueprint('admin', __name__)

# Mock data for demonstration (in production, use database)
mock_leads = [
    {
        'id': 1,
        'name': 'João Silva',
        'email': 'joao.silva@empresa.pt',
        'company': 'TechStart Lda',
        'message': 'Interessado em automação de processos',
        'phone': '+351 912 345 678',
        'score': 85,
        'classification': 'HOT',
        'source': 'contact_form',
        'created_at': '2025-08-10T10:30:00Z',
        'updated_at': '2025-08-10T10:30:00Z',
        'status': 'new'
    },
    {
        'id': 2,
        'name': 'Maria Santos',
        'email': 'maria.santos@startup.pt',
        'company': 'InnovaTech',
        'message': 'Preciso de website profissional',
        'phone': '+351 913 456 789',
        'score': 65,
        'classification': 'WARM',
        'source': 'chat_widget',
        'created_at': '2025-08-11T14:15:00Z',
        'updated_at': '2025-08-11T14:15:00Z',
        'status': 'contacted'
    },
    {
        'id': 3,
        'name': 'Pedro Costa',
        'email': 'pedro.costa@consultoria.pt',
        'company': 'Costa Consulting',
        'message': 'Orçamento para marketing digital',
        'phone': '+351 914 567 890',
        'score': 45,
        'classification': 'COLD',
        'source': 'linkedin',
        'created_at': '2025-08-12T09:20:00Z',
        'updated_at': '2025-08-12T09:20:00Z',
        'status': 'qualified'
    }
]

mock_services = [
    {
        'id': 1,
        'name': 'Website Essencial',
        'description': 'Website profissional com design moderno',
        'price': 397,
        'category': 'setup',
        'features': ['Design responsivo', 'SEO básico', 'SSL incluído'],
        'active': True,
        'created_at': '2025-08-01T00:00:00Z'
    },
    {
        'id': 2,
        'name': 'Automação Starter',
        'description': 'Automação básica de processos',
        'price': 29,
        'category': 'saas',
        'features': ['Workflows básicos', 'Integrações simples', 'Suporte email'],
        'active': True,
        'created_at': '2025-08-01T00:00:00Z'
    }
]

@admin_bp.route('/admin/dashboard', methods=['GET'])
@require_auth
def dashboard():
    """Admin dashboard statistics"""
    try:
        # Calculate statistics
        total_leads = len(mock_leads)
        hot_leads = len([l for l in mock_leads if l['classification'] == 'HOT'])
        warm_leads = len([l for l in mock_leads if l['classification'] == 'WARM'])
        cold_leads = len([l for l in mock_leads if l['classification'] == 'COLD'])
        
        # Recent leads (last 7 days)
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_leads = [
            l for l in mock_leads 
            if datetime.fromisoformat(l['created_at'].replace('Z', '+00:00')) > seven_days_ago
        ]
        
        # Revenue calculation (mock)
        total_revenue = sum([s['price'] for s in mock_services if s['active']]) * 10  # Mock multiplier
        
        stats = {
            'leads': {
                'total': total_leads,
                'hot': hot_leads,
                'warm': warm_leads,
                'cold': cold_leads,
                'recent': len(recent_leads)
            },
            'services': {
                'total': len(mock_services),
                'active': len([s for s in mock_services if s['active']])
            },
            'revenue': {
                'total': total_revenue,
                'monthly': total_revenue / 12  # Mock monthly
            }
        }
        
        logger.info(f"Dashboard accessed by: {request.current_user['email']}")
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@admin_bp.route('/admin/leads', methods=['GET'])
@require_auth
def get_leads():
    """Get all leads with optional filtering"""
    try:
        # Get query parameters
        classification = request.args.get('classification')
        status = request.args.get('status')
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Filter leads
        filtered_leads = mock_leads.copy()
        
        if classification:
            filtered_leads = [l for l in filtered_leads if l['classification'] == classification.upper()]
        
        if status:
            filtered_leads = [l for l in filtered_leads if l['status'] == status.lower()]
        
        # Sort by created_at (newest first)
        filtered_leads.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Apply pagination
        total = len(filtered_leads)
        if limit:
            filtered_leads = filtered_leads[offset:offset + limit]
        
        return jsonify({
            'success': True,
            'data': {
                'leads': filtered_leads,
                'total': total,
                'offset': offset,
                'limit': limit
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get leads error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@admin_bp.route('/admin/leads/<int:lead_id>', methods=['GET'])
@require_auth
def get_lead(lead_id):
    """Get specific lead by ID"""
    try:
        lead = next((l for l in mock_leads if l['id'] == lead_id), None)
        
        if not lead:
            return jsonify({
                'success': False,
                'message': 'Lead not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': lead
        }), 200
        
    except Exception as e:
        logger.error(f"Get lead error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@admin_bp.route('/admin/leads/<int:lead_id>', methods=['PUT'])
@require_auth
def update_lead(lead_id):
    """Update lead information"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Find lead
        lead_index = next((i for i, l in enumerate(mock_leads) if l['id'] == lead_id), None)
        
        if lead_index is None:
            return jsonify({
                'success': False,
                'message': 'Lead not found'
            }), 404
        
        # Update allowed fields
        allowed_fields = ['status', 'classification', 'notes']
        for field in allowed_fields:
            if field in data:
                mock_leads[lead_index][field] = data[field]
        
        # Update timestamp
        mock_leads[lead_index]['updated_at'] = datetime.now().isoformat() + 'Z'
        
        logger.info(f"Lead {lead_id} updated by: {request.current_user['email']}")
        
        return jsonify({
            'success': True,
            'data': mock_leads[lead_index]
        }), 200
        
    except Exception as e:
        logger.error(f"Update lead error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@admin_bp.route('/admin/services', methods=['GET'])
@require_auth
def get_services():
    """Get all services"""
    try:
        return jsonify({
            'success': True,
            'data': mock_services
        }), 200
        
    except Exception as e:
        logger.error(f"Get services error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@admin_bp.route('/admin/services', methods=['POST'])
@require_auth
def create_service():
    """Create new service"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['name', 'description', 'price', 'category']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Field {field} is required'
                }), 400
        
        # Create new service
        new_service = {
            'id': max([s['id'] for s in mock_services]) + 1 if mock_services else 1,
            'name': data['name'],
            'description': data['description'],
            'price': data['price'],
            'category': data['category'],
            'features': data.get('features', []),
            'active': data.get('active', True),
            'created_at': datetime.now().isoformat() + 'Z'
        }
        
        mock_services.append(new_service)
        
        logger.info(f"Service created by: {request.current_user['email']}")
        
        return jsonify({
            'success': True,
            'data': new_service
        }), 201
        
    except Exception as e:
        logger.error(f"Create service error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@admin_bp.route('/admin/services/<int:service_id>', methods=['PUT'])
@require_auth
def update_service(service_id):
    """Update service information"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Find service
        service_index = next((i for i, s in enumerate(mock_services) if s['id'] == service_id), None)
        
        if service_index is None:
            return jsonify({
                'success': False,
                'message': 'Service not found'
            }), 404
        
        # Update allowed fields
        allowed_fields = ['name', 'description', 'price', 'category', 'features', 'active']
        for field in allowed_fields:
            if field in data:
                mock_services[service_index][field] = data[field]
        
        logger.info(f"Service {service_id} updated by: {request.current_user['email']}")
        
        return jsonify({
            'success': True,
            'data': mock_services[service_index]
        }), 200
        
    except Exception as e:
        logger.error(f"Update service error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@admin_bp.route('/admin/services/<int:service_id>', methods=['DELETE'])
@require_auth
def delete_service(service_id):
    """Delete service"""
    try:
        # Find service
        service_index = next((i for i, s in enumerate(mock_services) if s['id'] == service_id), None)
        
        if service_index is None:
            return jsonify({
                'success': False,
                'message': 'Service not found'
            }), 404
        
        # Remove service
        deleted_service = mock_services.pop(service_index)
        
        logger.info(f"Service {service_id} deleted by: {request.current_user['email']}")
        
        return jsonify({
            'success': True,
            'message': 'Service deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Delete service error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


#!/usr/bin/env python3
"""
CRSET Solutions - Backend Principal Integrado
Combina todos os componentes dos 3 ZIPs
"""

import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_compress import Compress
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Enable compression
Compress(app)

# Configure CORS for production
CORS(app, origins=[
    "http://localhost:3000",
    "https://crsetsolutions.com",
    "https://go.crsetsolutions.com",
    "https://chat.crsetsolutions.com",
    "https://ops.crsetsolutions.com"
])

# Importar serviços de automação e rotas
import sys
sys.path.append('/home/ubuntu/crset-backend-integrado')

try:
    from services.advanced_automation import AdvancedAutomation
    from services.email_automation import ResendEmailService
    from routes.chat import chat_bp
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    
    automation_service = AdvancedAutomation()
    email_service = ResendEmailService(os.getenv('RESEND_API_KEY', ''))
    
    # Registar blueprints
    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api')
    
    logger.info("Serviços de automação, autenticação e admin carregados com sucesso")
except ImportError as e:
    logger.warning(f"Serviços não disponíveis: {str(e)}")
    automation_service = None
    email_service = None

# Health check endpoint (conforme super prompt)
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint obrigatório"""
    return jsonify({
        'status': 'ok',
        'service': 'CRSET Solutions Backend',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat(),
        'environment': os.getenv('ENV', 'development'),
        'database': 'Postgres' if os.getenv('DATABASE_URL') else 'SQLite',
        'cors': os.getenv('CORS_ORIGINS', '').split(',')
    }), 200

# Contact form endpoint integrado
@app.route('/api/contact', methods=['POST'])
def contact():
    """Handle contact form submissions com automação"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['name', 'email', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Field {field} is required'
                }), 400
        
        # Adicionar timestamp e source
        lead_data = {
            **data,
            'created_at': datetime.now().isoformat(),
            'source': data.get('source', 'contact_form'),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', '')
        }
        
        # Log the contact form submission
        logger.info(f"Contact form submission: {json.dumps(lead_data, indent=2)}")
        
        # Processar com automação (se disponível)
        if automation_service:
            try:
                automation_result = automation_service.process_lead_with_automation(lead_data)
                logger.info(f"Automation result: {automation_result}")
            except Exception as e:
                logger.error(f"Automation error: {str(e)}")
        
        # Enviar emails (se disponível)
        if email_service:
            try:
                # Email para admin
                admin_result = email_service.send_lead_notification(lead_data)
                # Email para cliente
                client_result = email_service.send_lead_confirmation(lead_data)
                logger.info(f"Email results - Admin: {admin_result}, Client: {client_result}")
            except Exception as e:
                logger.error(f"Email error: {str(e)}")
        
        # TODO: Salvar na base de dados (Postgres)
        # TODO: Integrar com Notion CRM
        
        return jsonify({
            'success': True,
            'message': 'Mensagem recebida! Entraremos em contacto em breve.',
            'lead_id': f"lead_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }), 200
        
    except Exception as e:
        logger.error(f"Error in contact endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500

# Services endpoint (do ZIP original)
@app.route('/api/services', methods=['GET'])
def services():
    """Get available services"""
    services_data = [
        {
            'id': 1,
            'name': 'Desenvolvimento Web',
            'description': 'Websites profissionais e responsivos',
            'price': 599,
            'currency': 'EUR',
            'mascot': 'laya',
            'features': [
                'Design responsivo',
                'SEO otimizado',
                'Integração CMS',
                'Suporte 6 meses'
            ]
        },
        {
            'id': 2,
            'name': 'Aplicações Mobile',
            'description': 'Apps iOS e Android nativas',
            'price': 799,
            'currency': 'EUR',
            'mascot': 'irina',
            'features': [
                'iOS & Android',
                'UI/UX profissional',
                'API integrada',
                'Publicação stores'
            ]
        },
        {
            'id': 3,
            'name': 'Automação de Processos',
            'description': 'Automatize tarefas e aumente produtividade',
            'price': 999,
            'currency': 'EUR',
            'mascot': 'boris',
            'popular': True,
            'features': [
                'Workflows automáticos',
                'Integração sistemas',
                'Dashboards',
                'ROI garantido'
            ]
        },
        {
            'id': 4,
            'name': 'E-commerce',
            'description': 'Lojas online completas e otimizadas',
            'price': 1299,
            'currency': 'EUR',
            'mascot': 'laya',
            'features': [
                'Pagamentos seguros',
                'Gestão stock',
                'Analytics',
                'Marketing integrado'
            ]
        },
        {
            'id': 5,
            'name': 'Soluções Cloud',
            'description': 'Infraestrutura escalável na nuvem',
            'price': 899,
            'currency': 'EUR',
            'mascot': 'boris',
            'features': [
                'AWS/Azure',
                'Backup automático',
                'Monitorização',
                'Escalabilidade'
            ]
        },
        {
            'id': 6,
            'name': 'Consultoria Tech',
            'description': 'Estratégia digital personalizada',
            'price': 1499,
            'currency': 'EUR',
            'mascot': 'irina',
            'features': [
                'Auditoria completa',
                'Roadmap estratégico',
                'Implementação',
                'Suporte contínuo'
            ]
        }
    ]
    
    return jsonify({
        'success': True,
        'services': services_data,
        'total': len(services_data)
    }), 200

# Root endpoint
@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'service': 'CRSET Solutions Backend Integrado',
        'version': '2.0.0',
        'status': 'running',
        'environment': os.getenv('ENV', 'development'),
        'endpoints': [
            '/health',
            '/api/contact',
            '/api/services'
        ]
    }), 200

if __name__ == '__main__':
    # Get configuration from environment
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('ENV') != 'production'
    
    # Log startup info (conforme super prompt)
    logger.info(f"ENV={os.getenv('ENV', 'development')}")
    logger.info(f"DB: {'Postgres' if os.getenv('DATABASE_URL') else 'SQLite'}")
    logger.info(f"CORS: {os.getenv('CORS_ORIGINS', '').split(',')}")
    logger.info(f"Starting CRSET Solutions Backend on {host}:{port}")
    
    # Run the application
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )


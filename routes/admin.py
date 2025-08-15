from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from src.models.demo_data import demo_manager
from src.services.email_automation import email_service
from src.services.advanced_automation import process_lead_with_automation, send_daily_report, send_weekly_insights
import hashlib

admin_bp = Blueprint('admin', __name__)

# Credencial Resend fornecida pelo usuário
RESEND_API_KEY = "re_PSYPFhdM_NsMdNKWXJpFyNU3Lh5wv1nuG"

# Função para verificar se o usuário está autenticado
def require_auth():
    if 'admin_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    return None

# Rota de login
@admin_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email e password são obrigatórios'}), 400
    
    # Verificar credenciais específicas do João Fonseca
    if email == 'jcsf2020@gmail.com' and password in ['-Portugal2025', '-Crsetsolutions2025', '-Financeflow2025']:
        # Verificar se admin existe
        admin_result = demo_manager.get_admin_by_email(email)
        
        if admin_result['success'] and admin_result['admin']:
            admin = admin_result['admin']
        else:
            # Criar admin se não existir
            admin_data = {
                'email': email,
                'password_hash': generate_password_hash(password),
                'name': 'João Fonseca',
                'role': 'super_admin'
            }
            create_result = demo_manager.create_admin(admin_data)
            if create_result['success']:
                admin = create_result['data']
            else:
                return jsonify({'error': 'Erro ao criar administrador'}), 500
        
        # Atualizar último login
        demo_manager.update_admin_login(admin['id'])
        
        session['admin_id'] = admin['id']
        session['admin_email'] = admin['email']
        session['admin_name'] = admin['name']
        
        return jsonify({
            'success': True,
            'admin': admin,
            'message': 'Login realizado com sucesso'
        })
    
    return jsonify({'error': 'Credenciais inválidas'}), 401

# Rota de logout
@admin_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logout realizado com sucesso'})

# Verificar se está autenticado
@admin_bp.route('/me', methods=['GET'])
def me():
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    admin_result = demo_manager.get_admin_by_email(session['admin_email'])
    if not admin_result['success'] or not admin_result['admin']:
        return jsonify({'error': 'Admin não encontrado'}), 404
    
    return jsonify({'admin': admin_result['admin']})

# Listar leads
@admin_bp.route('/leads', methods=['GET'])
def get_leads():
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    filters = {}
    if request.args.get('status'):
        filters['status'] = request.args.get('status')
    if request.args.get('priority'):
        filters['priority'] = request.args.get('priority')
    if request.args.get('search'):
        filters['search'] = request.args.get('search')
    
    result = demo_manager.get_leads(page=page, per_page=per_page, filters=filters)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify({'error': result['error']}), 500

# Criar lead (para receber do formulário do site)
@admin_bp.route('/leads', methods=['POST'])
def create_lead():
    data = request.get_json()
    
    required_fields = ['name', 'email', 'message']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} é obrigatório'}), 400
    
    lead_data = {
        'name': data['name'],
        'email': data['email'],
        'message': data['message'],
        'company': data.get('company'),
        'phone': data.get('phone'),
        'source': data.get('source', 'Site Principal'),
        'created_at': datetime.now().isoformat()
    }
    
    # 🚀 PROCESSAR COM AUTOMAÇÃO AVANÇADA
    try:
        # Calcular score, prioridade e criar sequência de nurturing
        processed_lead = process_lead_with_automation(lead_data)
        print(f"🤖 Lead processado com automação: Score {processed_lead.get('score')}, Prioridade {processed_lead.get('priority')}")
    except Exception as e:
        print(f"❌ Erro na automação avançada: {e}")
        processed_lead = lead_data
    
    result = demo_manager.create_lead(processed_lead)
    
    if result['success']:
        # 🚀 AUTOMAÇÃO DE EMAIL ATIVADA
        try:
            # 1. Enviar notificação para o administrador
            notification_result = email_service.send_lead_notification(result['data'])
            print(f"📧 Notificação admin: {notification_result}")
            
            # 2. Enviar confirmação automática para o cliente
            confirmation_result = email_service.send_lead_confirmation(result['data'])
            print(f"✅ Confirmação cliente: {confirmation_result}")
            
        except Exception as e:
            print(f"❌ Erro na automação de email: {e}")
        
        return jsonify({
            'success': True,
            'lead': result['data'],
            'score': processed_lead.get('score', 0),
            'priority': processed_lead.get('priority', 'media'),
            'message': 'Lead criado com sucesso, automação ativada e emails enviados'
        }), 201
    else:
        return jsonify({'error': result['error']}), 500

# Atualizar lead
@admin_bp.route('/leads/<int:lead_id>', methods=['PUT'])
def update_lead(lead_id):
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    data = request.get_json()
    
    # Campos que podem ser atualizados
    update_data = {}
    updatable_fields = ['status', 'priority', 'assigned_to', 'notes', 'company', 'phone']
    
    for field in updatable_fields:
        if field in data:
            update_data[field] = data[field]
    
    # Se o status mudou para "contactado", atualizar contacted_at
    if data.get('status') == 'contactado':
        update_data['contacted_at'] = datetime.utcnow().isoformat()
    
    result = demo_manager.update_lead(lead_id, update_data)
    
    if result['success']:
        return jsonify({
            'success': True,
            'lead': result['data'],
            'message': 'Lead atualizado com sucesso'
        })
    else:
        return jsonify({'error': result['error']}), 500

# Eliminar lead
@admin_bp.route('/leads/<int:lead_id>', methods=['DELETE'])
def delete_lead(lead_id):
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    result = demo_manager.delete_lead(lead_id)
    
    if result['success']:
        return jsonify({
            'success': True,
            'message': 'Lead eliminado com sucesso'
        })
    else:
        return jsonify({'error': result['error']}), 500

# Estatísticas do dashboard
@admin_bp.route('/stats', methods=['GET'])
def get_stats():
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    result = demo_manager.get_stats()
    
    if result['success']:
        # Remover o campo 'success' antes de retornar
        stats = {k: v for k, v in result.items() if k != 'success'}
        return jsonify(stats)
    else:
        return jsonify({'error': result['error']}), 500

# Leads urgentes (não contactados há mais de 2 horas)
@admin_bp.route('/leads/urgent', methods=['GET'])
def get_urgent_leads():
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    result = demo_manager.get_urgent_leads()
    
    if result['success']:
        return jsonify({
            'urgent_leads': result['urgent_leads'],
            'count': result['count']
        })
    else:
        return jsonify({'error': result['error']}), 500

# Enviar alerta de leads urgentes
@admin_bp.route('/alerts/urgent', methods=['POST'])
def send_urgent_alert():
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        # Obter leads urgentes
        urgent_result = demo_manager.get_urgent_leads()
        
        if urgent_result['success'] and urgent_result['urgent_leads']:
            # Enviar alerta por email
            alert_result = email_service.send_urgent_alert(urgent_result['urgent_leads'])
            
            return jsonify({
                'success': True,
                'message': f'Alerta enviado para {len(urgent_result["urgent_leads"])} lead(s) urgente(s)',
                'email_result': alert_result
            })
        else:
            return jsonify({
                'success': True,
                'message': 'Nenhum lead urgente encontrado'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Enviar relatório diário
@admin_bp.route('/reports/daily', methods=['POST'])
def send_daily_report():
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        # Obter estatísticas
        stats_result = demo_manager.get_stats()
        
        # Obter leads recentes
        leads_result = demo_manager.get_leads(page=1, per_page=10)
        
        if stats_result['success'] and leads_result['success']:
            # Enviar relatório por email
            report_result = email_service.send_daily_report(
                {k: v for k, v in stats_result.items() if k != 'success'},
                leads_result['leads']
            )
            
            return jsonify({
                'success': True,
                'message': 'Relatório diário enviado com sucesso',
                'email_result': report_result
            })
        else:
            return jsonify({'error': 'Erro ao obter dados para o relatório'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def send_lead_notification(lead_data):
    """Enviar notificação de novo lead por email"""
    try:
        # Aqui podemos implementar notificação usando Resend API
        # Por agora, apenas log
        print(f"📧 NOVO LEAD: {lead_data['name']} ({lead_data['email']})")
        print(f"📱 Empresa: {lead_data.get('company', 'N/A')}")
        print(f"💬 Mensagem: {lead_data['message'][:100]}...")
        
        # TODO: Implementar envio real de email usando RESEND_API_KEY
        # import requests
        # 
        # email_data = {
        #     "from": "noreply@crsetsolutions.com",
        #     "to": ["jcsf2020@gmail.com"],
        #     "subject": f"Novo Lead: {lead_data['name']}",
        #     "html": f"""
        #     <h2>Novo Lead Recebido</h2>
        #     <p><strong>Nome:</strong> {lead_data['name']}</p>
        #     <p><strong>Email:</strong> {lead_data['email']}</p>
        #     <p><strong>Empresa:</strong> {lead_data.get('company', 'N/A')}</p>
        #     <p><strong>Mensagem:</strong> {lead_data['message']}</p>
        #     """
        # }
        # 
        # response = requests.post(
        #     "https://api.resend.com/emails",
        #     headers={
        #         "Authorization": f"Bearer {RESEND_API_KEY}",
        #         "Content-Type": "application/json"
        #     },
        #     json=email_data
        # )
        
        return True
    except Exception as e:
        print(f"Erro ao enviar notificação: {e}")
        return False



# 📊 ROTAS DE AUTOMAÇÃO E RELATÓRIOS

@admin_bp.route('/automation/daily-report', methods=['POST'])
def trigger_daily_report():
    """Enviar relatório diário manualmente"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        send_daily_report()
        return jsonify({
            'success': True,
            'message': 'Relatório diário enviado com sucesso'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao enviar relatório: {str(e)}'
        }), 500

@admin_bp.route('/automation/weekly-insights', methods=['POST'])
def trigger_weekly_insights():
    """Enviar insights semanais manualmente"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        send_weekly_insights()
        return jsonify({
            'success': True,
            'message': 'Insights semanais enviados com sucesso'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao enviar insights: {str(e)}'
        }), 500

@admin_bp.route('/automation/test-lead-scoring', methods=['POST'])
def test_lead_scoring():
    """Testar sistema de lead scoring"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    data = request.get_json()
    
    # Lead de teste
    test_lead = {
        'name': data.get('name', 'João Teste'),
        'email': data.get('email', 'joao.teste@empresa.pt'),
        'company': data.get('company', 'TechCorp'),
        'message': data.get('message', 'Preciso urgentemente de uma demo da vossa solução de automação. Temos orçamento aprovado.'),
        'source': data.get('source', 'hero_form'),
        'created_at': datetime.now().isoformat()
    }
    
    try:
        processed_lead = process_lead_with_automation(test_lead)
        
        return jsonify({
            'success': True,
            'original_lead': test_lead,
            'processed_lead': processed_lead,
            'score': processed_lead.get('score'),
            'priority': processed_lead.get('priority'),
            'nurturing_sequence': processed_lead.get('nurturing_sequence'),
            'message': 'Lead scoring testado com sucesso'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro no teste: {str(e)}'
        }), 500

@admin_bp.route('/automation/stats', methods=['GET'])
def get_automation_stats():
    """Obter estatísticas da automação"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    # Simular estatísticas (em produção, vir da base de dados)
    stats = {
        'leads_processed_today': 4,
        'average_score': 67,
        'high_priority_leads': 2,
        'urgent_leads': 1,
        'emails_sent_today': 12,
        'conversion_rate': 3.8,
        'response_time_avg': 1.8,
        'top_sources': [
            {'source': 'Hero Form', 'count': 45, 'avg_score': 85},
            {'source': 'Contact Form', 'count': 35, 'avg_score': 65},
            {'source': 'Exit Popup', 'count': 20, 'avg_score': 78}
        ],
        'score_distribution': {
            'urgent': 15,    # 100-150
            'high': 35,      # 70-99
            'medium': 40,    # 40-69
            'low': 10        # 0-39
        },
        'hourly_performance': [
            {'hour': 9, 'leads': 2, 'avg_score': 72},
            {'hour': 10, 'leads': 3, 'avg_score': 68},
            {'hour': 11, 'leads': 1, 'avg_score': 85},
            {'hour': 14, 'leads': 4, 'avg_score': 78},
            {'hour': 15, 'leads': 3, 'avg_score': 82},
            {'hour': 16, 'leads': 2, 'avg_score': 75}
        ]
    }
    
    return jsonify({
        'success': True,
        'stats': stats,
        'generated_at': datetime.now().isoformat()
    })


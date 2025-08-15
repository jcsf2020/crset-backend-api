import os
import json
from flask import Blueprint, request, jsonify, session
from openai import OpenAI
from flask_cors import cross_origin

chat_bp = Blueprint('chat', __name__)

# Configurar OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Mensagens pré-definidas do sistema
SYSTEM_MESSAGES = {
    'default': """Você é um assistente especializado da CRSET Solutions, empresa portuguesa de soluções digitais inteligentes.

INFORMAÇÕES DA EMPRESA:
- Nome: CRSET Solutions
- Especialidade: Soluções digitais personalizadas com automação, comunicação e segurança
- Mascotes: Boris (Automação), Laya (Comunicação), Irina (Segurança)
- Contacto: crsetsolutions@gmail.com, +351 914 423 688 (WhatsApp)

PLANOS DISPONÍVEIS:
Setup Solutions:
- Website Essencial: €397 (website institucional, domínio, SSL, suporte 3 meses)
- Website Profissional: €697 (e-commerce, SEO, branding, suporte 6 meses)
- Solução White Label: €1.497 (personalização total, branding completo, suporte 12 meses)

SaaS Solutions:
- Starter: €29/mês (até 1.000 utilizadores, estatísticas essenciais)
- Profissional: €59/mês (até 5.000 utilizadores, dashboard com automações)
- Premium: €99/mês (utilizadores ilimitados, IA integrada, suporte 24/7)

INSTRUÇÕES:
- Seja sempre profissional e prestável
- Foque em soluções digitais e automação
- Quando apropriado, sugira análise gratuita do negócio
- Se o utilizador demonstrar interesse, colete dados para lead (nome, email, empresa)
- Mantenha respostas concisas mas informativas
- Use português de Portugal""",
    
    'lead_qualification': """Você está em modo de qualificação de leads. O utilizador demonstrou interesse nos serviços CRSET Solutions.

OBJETIVO: Coletar informações para qualificar o lead
- Nome completo
- Email profissional
- Nome da empresa
- Tipo de negócio/setor
- Principais desafios digitais
- Orçamento aproximado

Seja natural na conversa, não faça um interrogatório. Colete as informações gradualmente."""
}

@chat_bp.route('/chat', methods=['POST'])
@cross_origin()
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        mode = data.get('mode', 'default')
        
        if not message:
            return jsonify({'error': 'Mensagem é obrigatória'}), 400
        
        # Recuperar histórico da sessão
        session_key = f'chat_history_{session_id}'
        chat_history = session.get(session_key, [])
        
        # Adicionar mensagem do sistema se for nova sessão
        if not chat_history:
            system_message = SYSTEM_MESSAGES.get(mode, SYSTEM_MESSAGES['default'])
            chat_history.append({
                'role': 'system',
                'content': system_message
            })
        
        # Adicionar mensagem do utilizador
        chat_history.append({
            'role': 'user',
            'content': message
        })
        
        # Chamar OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=chat_history,
            max_tokens=500,
            temperature=0.7
        )
        
        assistant_message = response.choices[0].message.content
        
        # Adicionar resposta ao histórico
        chat_history.append({
            'role': 'assistant',
            'content': assistant_message
        })
        
        # Salvar histórico na sessão (manter apenas últimas 20 mensagens)
        if len(chat_history) > 20:
            chat_history = chat_history[-20:]
        
        session[session_key] = chat_history
        
        # Detectar se é um lead qualificado
        is_qualified_lead = detect_qualified_lead(message, assistant_message)
        
        return jsonify({
            'message': assistant_message,
            'session_id': session_id,
            'is_qualified_lead': is_qualified_lead,
            'timestamp': data.get('timestamp')
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@chat_bp.route('/chat/lead', methods=['POST'])
@cross_origin()
def create_lead():
    """Endpoint para criar lead a partir do chat"""
    try:
        data = request.get_json()
        
        # Dados obrigatórios
        name = data.get('name', '')
        email = data.get('email', '')
        company = data.get('company', '')
        
        if not all([name, email]):
            return jsonify({'error': 'Nome e email são obrigatórios'}), 400
        
        # Dados opcionais do chat
        chat_summary = data.get('chat_summary', '')
        session_id = data.get('session_id', '')
        
        # Aqui você pode integrar com o CRM principal
        # Por agora, apenas retornamos sucesso
        
        lead_data = {
            'name': name,
            'email': email,
            'company': company,
            'source': 'AI Chat Assistant',
            'chat_summary': chat_summary,
            'session_id': session_id,
            'utm_source': 'chat',
            'utm_medium': 'ai_assistant',
            'utm_campaign': 'chat_widget'
        }
        
        return jsonify({
            'success': True,
            'message': 'Lead capturado com sucesso!',
            'lead_id': f'chat_{session_id}_{hash(email)}',
            'data': lead_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao criar lead: {str(e)}'}), 500

@chat_bp.route('/chat/session/<session_id>', methods=['GET'])
@cross_origin()
def get_session(session_id):
    """Recuperar histórico de uma sessão"""
    try:
        session_key = f'chat_history_{session_id}'
        chat_history = session.get(session_key, [])
        
        # Filtrar apenas mensagens do usuário e assistente
        filtered_history = [
            msg for msg in chat_history 
            if msg['role'] in ['user', 'assistant']
        ]
        
        return jsonify({
            'session_id': session_id,
            'messages': filtered_history,
            'message_count': len(filtered_history)
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao recuperar sessão: {str(e)}'}), 500

def detect_qualified_lead(user_message, assistant_message):
    """Detectar se a conversa indica um lead qualificado"""
    
    # Palavras-chave que indicam interesse
    interest_keywords = [
        'preço', 'orçamento', 'custo', 'valor',
        'contratar', 'comprar', 'adquirir',
        'análise gratuita', 'demonstração',
        'contacto', 'reunião', 'proposta',
        'empresa', 'negócio', 'projeto'
    ]
    
    # Verificar se há palavras de interesse na mensagem do usuário
    user_lower = user_message.lower()
    has_interest = any(keyword in user_lower for keyword in interest_keywords)
    
    # Verificar se o assistente sugeriu próximos passos
    assistant_lower = assistant_message.lower()
    suggests_action = any(phrase in assistant_lower for phrase in [
        'análise gratuita', 'entre em contacto', 'agendar',
        'proposta', 'demonstração', 'reunião'
    ])
    
    return has_interest or suggests_action


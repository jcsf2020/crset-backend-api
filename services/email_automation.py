import requests
import json
from datetime import datetime
from typing import Dict, List, Optional

class ResendEmailService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.resend.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def send_lead_notification(self, lead_data: Dict) -> Dict:
        """Enviar notificação de novo lead para o administrador"""
        try:
            email_data = {
                "from": "CRSET Solutions <noreply@crsetsolutions.com>",
                "to": ["jcsf2020@gmail.com"],
                "subject": f"🚨 Novo Lead: {lead_data['name']} - {lead_data.get('company', 'Sem empresa')}",
                "html": self._generate_lead_notification_html(lead_data)
            }
            
            response = requests.post(
                f"{self.base_url}/emails",
                headers=self.headers,
                json=email_data
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Erro {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    def send_lead_confirmation(self, lead_data: Dict) -> Dict:
        """Enviar confirmação automática para o cliente"""
        try:
            email_data = {
                "from": "João Fonseca - CRSET Solutions <joao@crsetsolutions.com>",
                "to": [lead_data['email']],
                "subject": "Obrigado pelo seu contacto - CRSET Solutions",
                "html": self._generate_lead_confirmation_html(lead_data)
            }
            
            response = requests.post(
                f"{self.base_url}/emails",
                headers=self.headers,
                json=email_data
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Erro {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    def send_urgent_alert(self, urgent_leads: List[Dict]) -> Dict:
        """Enviar alerta de leads urgentes"""
        try:
            if not urgent_leads:
                return {"success": True, "message": "Nenhum lead urgente"}
            
            email_data = {
                "from": "CRSET Solutions Alert <alert@crsetsolutions.com>",
                "to": ["jcsf2020@gmail.com"],
                "subject": f"⚠️ ALERTA: {len(urgent_leads)} Lead(s) Urgente(s) Precisam Atenção",
                "html": self._generate_urgent_alert_html(urgent_leads)
            }
            
            response = requests.post(
                f"{self.base_url}/emails",
                headers=self.headers,
                json=email_data
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Erro {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    def send_daily_report(self, stats: Dict, recent_leads: List[Dict]) -> Dict:
        """Enviar relatório diário"""
        try:
            email_data = {
                "from": "CRSET Solutions Reports <reports@crsetsolutions.com>",
                "to": ["jcsf2020@gmail.com"],
                "subject": f"📊 Relatório Diário - {datetime.now().strftime('%d/%m/%Y')}",
                "html": self._generate_daily_report_html(stats, recent_leads)
            }
            
            response = requests.post(
                f"{self.base_url}/emails",
                headers=self.headers,
                json=email_data
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Erro {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _generate_lead_notification_html(self, lead_data: Dict) -> str:
        """Gerar HTML para notificação de novo lead"""
        priority_colors = {
            'baixa': '#6B7280',
            'media': '#3B82F6',
            'alta': '#F59E0B',
            'urgente': '#EF4444'
        }
        
        priority_color = priority_colors.get(lead_data.get('priority', 'media'), '#3B82F6')
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Novo Lead - CRSET Solutions</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px;">
                <h1 style="color: white; margin: 0; font-size: 28px;">🚨 Novo Lead Recebido</h1>
                <p style="color: #E5E7EB; margin: 10px 0 0 0; font-size: 16px;">CRSET Solutions Dashboard</p>
            </div>
            
            <div style="background: #F9FAFB; padding: 25px; border-radius: 8px; border-left: 4px solid {priority_color}; margin-bottom: 20px;">
                <h2 style="margin: 0 0 15px 0; color: #1F2937; font-size: 22px;">👤 {lead_data['name']}</h2>
                <div style="display: grid; gap: 10px;">
                    <p style="margin: 0;"><strong>📧 Email:</strong> <a href="mailto:{lead_data['email']}" style="color: #3B82F6; text-decoration: none;">{lead_data['email']}</a></p>
                    <p style="margin: 0;"><strong>🏢 Empresa:</strong> {lead_data.get('company', 'Não informado')}</p>
                    <p style="margin: 0;"><strong>📱 Telefone:</strong> {lead_data.get('phone', 'Não informado')}</p>
                    <p style="margin: 0;"><strong>🌐 Fonte:</strong> {lead_data.get('source', 'Site Principal')}</p>
                    <p style="margin: 0;"><strong>⚡ Prioridade:</strong> <span style="background: {priority_color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; text-transform: uppercase;">{lead_data.get('priority', 'média')}</span></p>
                </div>
            </div>
            
            <div style="background: white; padding: 25px; border-radius: 8px; border: 1px solid #E5E7EB; margin-bottom: 20px;">
                <h3 style="margin: 0 0 15px 0; color: #1F2937;">💬 Mensagem:</h3>
                <p style="margin: 0; background: #F3F4F6; padding: 15px; border-radius: 6px; font-style: italic; line-height: 1.6;">"{lead_data['message']}"</p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="http://localhost:5000" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block; font-size: 16px;">🚀 Aceder ao Dashboard</a>
            </div>
            
            <div style="background: #FEF3C7; border: 1px solid #F59E0B; padding: 15px; border-radius: 6px; margin: 20px 0;">
                <p style="margin: 0; color: #92400E; font-size: 14px;"><strong>⏰ Ação Recomendada:</strong> Contactar o lead nas próximas 2 horas para maximizar a taxa de conversão.</p>
            </div>
            
            <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 30px 0;">
            
            <div style="text-align: center; color: #6B7280; font-size: 12px;">
                <p style="margin: 0;">CRSET Solutions - Dashboard Administrativo</p>
                <p style="margin: 5px 0 0 0;">Recebido em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
            </div>
        </body>
        </html>
        """

    def _generate_lead_confirmation_html(self, lead_data: Dict) -> str:
        """Gerar HTML para confirmação automática ao cliente"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Obrigado pelo contacto - CRSET Solutions</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px;">
                <h1 style="color: white; margin: 0; font-size: 28px;">✅ Mensagem Recebida</h1>
                <p style="color: #E5E7EB; margin: 10px 0 0 0; font-size: 16px;">CRSET Solutions</p>
            </div>
            
            <div style="background: #F9FAFB; padding: 25px; border-radius: 8px; margin-bottom: 20px;">
                <h2 style="margin: 0 0 15px 0; color: #1F2937;">Olá {lead_data['name']},</h2>
                <p style="margin: 0 0 15px 0; font-size: 16px;">Obrigado por entrar em contacto connosco! Recebemos a sua mensagem e iremos responder brevemente.</p>
                <p style="margin: 0; font-size: 16px;">A nossa equipa irá analisar o seu pedido e contactá-lo nas próximas 24 horas.</p>
            </div>
            
            <div style="background: white; padding: 25px; border-radius: 8px; border: 1px solid #E5E7EB; margin-bottom: 20px;">
                <h3 style="margin: 0 0 15px 0; color: #1F2937;">📋 Resumo do seu contacto:</h3>
                <div style="background: #F3F4F6; padding: 15px; border-radius: 6px;">
                    <p style="margin: 0 0 10px 0;"><strong>Nome:</strong> {lead_data['name']}</p>
                    <p style="margin: 0 0 10px 0;"><strong>Email:</strong> {lead_data['email']}</p>
                    <p style="margin: 0 0 10px 0;"><strong>Empresa:</strong> {lead_data.get('company', 'Não informado')}</p>
                    <p style="margin: 0;"><strong>Mensagem:</strong> "{lead_data['message'][:100]}{'...' if len(lead_data['message']) > 100 else ''}"</p>
                </div>
            </div>
            
            <div style="background: #EBF8FF; border: 1px solid #3B82F6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin: 0 0 10px 0; color: #1E40AF;">🚀 Sobre a CRSET Solutions</h3>
                <p style="margin: 0 0 10px 0; color: #1E3A8A;">Somos especialistas em soluções de Inteligência Artificial e automação para empresas que querem crescer e inovar.</p>
                <p style="margin: 0; color: #1E3A8A;"><strong>Principais serviços:</strong> Chatbots, Automação de Processos, Análise de Dados, Consultoria em IA</p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="https://crsetsolutions.com" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block; font-size: 16px;">🌐 Visitar Website</a>
            </div>
            
            <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 30px 0;">
            
            <div style="text-align: center; color: #6B7280; font-size: 12px;">
                <p style="margin: 0;"><strong>João Fonseca</strong> - Fundador & CEO</p>
                <p style="margin: 5px 0;">CRSET Solutions</p>
                <p style="margin: 5px 0;">📧 joao@crsetsolutions.com | 🌐 crsetsolutions.com</p>
                <p style="margin: 15px 0 0 0; font-size: 11px; color: #9CA3AF;">Esta é uma resposta automática. Se precisar de assistência imediata, responda a este email.</p>
            </div>
        </body>
        </html>
        """

    def _generate_urgent_alert_html(self, urgent_leads: List[Dict]) -> str:
        """Gerar HTML para alerta de leads urgentes"""
        leads_html = ""
        for lead in urgent_leads:
            leads_html += f"""
            <div style="background: #FEF2F2; border: 1px solid #EF4444; padding: 15px; border-radius: 6px; margin: 10px 0;">
                <h4 style="margin: 0 0 10px 0; color: #DC2626;">{lead['name']} - {lead.get('company', 'Sem empresa')}</h4>
                <p style="margin: 0 0 5px 0; font-size: 14px;"><strong>Email:</strong> {lead['email']}</p>
                <p style="margin: 0 0 5px 0; font-size: 14px;"><strong>Criado:</strong> {lead['created_at']}</p>
                <p style="margin: 0; font-size: 14px;"><strong>Mensagem:</strong> {lead['message'][:100]}...</p>
            </div>
            """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Alerta de Leads Urgentes - CRSET Solutions</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px;">
                <h1 style="color: white; margin: 0; font-size: 28px;">⚠️ ALERTA URGENTE</h1>
                <p style="color: #FEE2E2; margin: 10px 0 0 0; font-size: 16px;">{len(urgent_leads)} Lead(s) Precisam Atenção Imediata</p>
            </div>
            
            <div style="background: #FEF3C7; border: 1px solid #F59E0B; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <p style="margin: 0; color: #92400E; font-weight: bold;">⏰ Estes leads não foram contactados há mais de 2 horas e podem estar perdendo interesse.</p>
            </div>
            
            {leads_html}
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="http://localhost:5000" style="background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block; font-size: 16px;">🚨 Aceder ao Dashboard</a>
            </div>
            
            <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 30px 0;">
            
            <div style="text-align: center; color: #6B7280; font-size: 12px;">
                <p style="margin: 0;">CRSET Solutions - Sistema de Alertas</p>
                <p style="margin: 5px 0 0 0;">Enviado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
            </div>
        </body>
        </html>
        """

    def _generate_daily_report_html(self, stats: Dict, recent_leads: List[Dict]) -> str:
        """Gerar HTML para relatório diário"""
        recent_leads_html = ""
        for lead in recent_leads[:5]:  # Mostrar apenas os 5 mais recentes
            status_colors = {
                'novo': '#3B82F6',
                'contactado': '#F59E0B',
                'qualificado': '#10B981',
                'convertido': '#8B5CF6',
                'perdido': '#EF4444'
            }
            status_color = status_colors.get(lead.get('status', 'novo'), '#3B82F6')
            
            recent_leads_html += f"""
            <tr style="border-bottom: 1px solid #E5E7EB;">
                <td style="padding: 10px; font-size: 14px;">{lead['name']}</td>
                <td style="padding: 10px; font-size: 14px;">{lead.get('company', 'N/A')}</td>
                <td style="padding: 10px; font-size: 14px;"><span style="background: {status_color}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{lead.get('status', 'novo').upper()}</span></td>
            </tr>
            """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Relatório Diário - CRSET Solutions</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px;">
                <h1 style="color: white; margin: 0; font-size: 28px;">📊 Relatório Diário</h1>
                <p style="color: #E5E7EB; margin: 10px 0 0 0; font-size: 16px;">{datetime.now().strftime('%d de %B de %Y')}</p>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 30px;">
                <div style="background: #EBF8FF; padding: 20px; border-radius: 8px; text-align: center;">
                    <h3 style="margin: 0; color: #1E40AF; font-size: 32px;">{stats.get('total_leads', 0)}</h3>
                    <p style="margin: 5px 0 0 0; color: #3B82F6; font-weight: bold;">Total de Leads</p>
                </div>
                <div style="background: #F0FDF4; padding: 20px; border-radius: 8px; text-align: center;">
                    <h3 style="margin: 0; color: #166534; font-size: 32px;">{stats.get('leads_hoje', 0)}</h3>
                    <p style="margin: 5px 0 0 0; color: #10B981; font-weight: bold;">Leads Hoje</p>
                </div>
                <div style="background: #FEF3C7; padding: 20px; border-radius: 8px; text-align: center;">
                    <h3 style="margin: 0; color: #92400E; font-size: 32px;">{stats.get('leads_semana', 0)}</h3>
                    <p style="margin: 5px 0 0 0; color: #F59E0B; font-weight: bold;">Esta Semana</p>
                </div>
                <div style="background: #F3E8FF; padding: 20px; border-radius: 8px; text-align: center;">
                    <h3 style="margin: 0; color: #6B21A8; font-size: 32px;">{stats.get('leads_mes', 0)}</h3>
                    <p style="margin: 5px 0 0 0; color: #8B5CF6; font-weight: bold;">Este Mês</p>
                </div>
            </div>
            
            <div style="background: white; padding: 25px; border-radius: 8px; border: 1px solid #E5E7EB; margin-bottom: 20px;">
                <h3 style="margin: 0 0 15px 0; color: #1F2937;">📋 Leads Recentes</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: #F9FAFB;">
                            <th style="padding: 10px; text-align: left; font-size: 12px; color: #6B7280; text-transform: uppercase;">Nome</th>
                            <th style="padding: 10px; text-align: left; font-size: 12px; color: #6B7280; text-transform: uppercase;">Empresa</th>
                            <th style="padding: 10px; text-align: left; font-size: 12px; color: #6B7280; text-transform: uppercase;">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {recent_leads_html}
                    </tbody>
                </table>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="http://localhost:5000" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block; font-size: 16px;">📊 Ver Dashboard Completo</a>
            </div>
            
            <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 30px 0;">
            
            <div style="text-align: center; color: #6B7280; font-size: 12px;">
                <p style="margin: 0;">CRSET Solutions - Relatórios Automáticos</p>
                <p style="margin: 5px 0 0 0;">Gerado automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
            </div>
        </body>
        </html>
        """

# Instância global do serviço de email
RESEND_API_KEY = "re_PSYPFhdM_NsMdNKWXJpFyNU3Lh5wv1nuG"
email_service = ResendEmailService(RESEND_API_KEY)


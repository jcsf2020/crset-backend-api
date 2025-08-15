import os
from flask import Flask, jsonify
from flask_cors import CORS

ALLOWED_ORIGINS = [
    "https://crsetsolutions.com",
    "https://go.crsetsolutions.com",
    "https://chat.crsetsolutions.com",
    "https://ops.crsetsolutions.com",
]

def create_app():
    app = Flask(__name__)
    CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=True)

    @app.get("/health")
    def health():
        return jsonify(
            status="ok",
            service="crset-backend-api",
            env=os.getenv("ENV", "production"),
            version=os.getenv("RAILWAY_DEPLOYMENT_ID", "unknown"),
        ), 200

    # Rotas reais — manter imports pesados dentro das rotas (lazy) para não travar o boot
    @app.post("/api/chat")
    def api_chat():
        from openai import OpenAI  # import lazy
        # ... implementar lógica real já existente (não remover a vossa)
        return jsonify({"status": "ok"}), 200

    @app.post("/api/contact")
    def api_contact():
        # import lazy do resend, db, etc, se necessário
        return jsonify({"status": "ok"}), 200

    return app

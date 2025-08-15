import os

# Arranque ultra-rápido: não importar nada pesado aqui.
# O create_app só monta rotas essenciais de imediato.
from src.main import create_app

app = create_app()

# Opcional: log básico para confirmar boot
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)


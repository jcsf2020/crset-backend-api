# wsgi.py - Fallback Waitress
import os
from src.main import app  # garante import explícito do objeto Flask

if __name__ == "__main__":
    from waitress import serve
    port = int(os.getenv("PORT", "8000"))
    serve(app, host="0.0.0.0", port=port, threads=16)


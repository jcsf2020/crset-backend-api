# wsgi.py
import os
from src.main import app  # garante import explícito do objeto Flask

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))


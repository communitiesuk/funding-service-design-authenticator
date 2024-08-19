from pathlib import Path

from app import app

if __name__ == "__main__":
    app.run(f"{Path(__file__).stem}:app", host="0.0.0.0", port=8080)

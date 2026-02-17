from src.entrypoints.app import create_app
from src.entrypoints.config import Config

app = create_app()

if __name__ == '__main__':
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.FLASK_DEBUG
    )

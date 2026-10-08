from flask import Flask, jsonify

from app.db import default_db_path, init_db
from app.routes import bp


def create_app(db_path=None):
    app = Flask(__name__)
    path = db_path or default_db_path()
    app.config["DB_PATH"] = path
    init_db(path)
    app.register_blueprint(bp)

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "ruta no encontrada"}), 404

    @app.errorhandler(405)
    def method_not_allowed(_error):
        return jsonify({"error": "metodo no permitido"}), 405

    return app

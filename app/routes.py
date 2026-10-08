from flask import Blueprint, current_app, jsonify, request

from app.db import create_user, delete_user, get_user, list_users, update_user
from app.settings import APP_MESSAGE
from app.validation import parse_user

bp = Blueprint("api", __name__)


def _db():
    return current_app.config["DB_PATH"]


def _error(message, status):
    return jsonify({"error": message}), status


@bp.get("/api/health")
def health():
    return jsonify({"status": "ok", "message": APP_MESSAGE}), 200


@bp.get("/api/users")
def get_users():
    return jsonify(list_users(_db())), 200


@bp.post("/api/users")
def post_user():
    payload, message = parse_user(request.get_json(silent=True))
    if message:
        return _error(message, 400)

    user = create_user(_db(), payload["name"], payload["email"])
    if user is None:
        return _error("email duplicado", 409)
    return jsonify(user), 201


@bp.get("/api/users/<int:user_id>")
def get_user_by_id(user_id):
    user = get_user(_db(), user_id)
    if user is None:
        return _error("usuario no encontrado", 404)
    return jsonify(user), 200


@bp.put("/api/users/<int:user_id>")
def put_user(user_id):
    payload, message = parse_user(request.get_json(silent=True))
    if message:
        return _error(message, 400)

    result = update_user(_db(), user_id, payload["name"], payload["email"])
    if result == "missing":
        return _error("usuario no encontrado", 404)
    if result == "duplicate":
        return _error("email duplicado", 409)
    return jsonify(result), 200


@bp.delete("/api/users/<int:user_id>")
def remove_user(user_id):
    if not delete_user(_db(), user_id):
        return _error("usuario no encontrado", 404)
    return jsonify({"deleted": True, "id": user_id}), 200

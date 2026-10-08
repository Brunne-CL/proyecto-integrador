"""Validacion del body de usuario. No depende de Flask ni de la base de datos."""


def parse_user(data):
    """Devuelve ({name, email}, None) o (None, mensaje de error)."""
    if not isinstance(data, dict):
        return None, "el body debe ser un objeto JSON"

    if "name" not in data or "email" not in data:
        return None, "name y email son requeridos"

    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        return None, "name debe ser un texto no vacio"
    name = name.strip()
    if len(name) > 100:
        return None, "name no puede superar 100 caracteres"

    email = data.get("email")
    if not isinstance(email, str):
        return None, "email con formato invalido"
    email = email.strip().lower()
    if not _valid_email(email):
        return None, "email con formato invalido"
    if len(email) > 254:
        return None, "email con formato invalido"

    return {"name": name, "email": email}, None


def _valid_email(email):
    if email.count("@") != 1:
        return False
    local, domain = email.split("@")
    if not local or not domain:
        return False
    if "." not in domain or domain.startswith(".") or domain.endswith("."):
        return False
    return " " not in email

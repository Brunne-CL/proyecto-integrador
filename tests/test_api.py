"""Pruebas de integracion de los 6 endpoints."""

from app.settings import APP_MESSAGE

ENDPOINTS = {
    ("GET", "/api/health"),
    ("GET", "/api/users"),
    ("POST", "/api/users"),
    ("GET", "/api/users/<int:user_id>"),
    ("PUT", "/api/users/<int:user_id>"),
    ("DELETE", "/api/users/<int:user_id>"),
}


def body(res):
    assert res.is_json
    return res.get_json()


def crear(client, name="Ana", email="ana@example.com"):
    res = client.post("/api/users", json={"name": name, "email": email})
    assert res.status_code == 201
    return body(res)


def test_hay_exactamente_seis_endpoints(client):
    found = set()
    for rule in client.application.url_map.iter_rules():
        if not rule.rule.startswith("/api"):
            continue
        methods = rule.methods - {"HEAD", "OPTIONS"}
        for method in methods:
            found.add((method, rule.rule))
    assert found == ENDPOINTS
    assert len(found) == 6


def test_health(client):
    data = body(client.get("/api/health"))
    assert data == {"status": "ok", "message": APP_MESSAGE}


def test_lista_vacia(client):
    assert body(client.get("/api/users")) == []


def test_crea_lista_y_consulta_usuario(client):
    ana = crear(client)
    luis = crear(client, "Luis", "luis@example.com")

    assert body(client.get("/api/users")) == [ana, luis]
    assert body(client.get(f"/api/users/{ana['id']}")) == ana


def test_crea_normaliza_espacios_y_email(client):
    data = body(client.post("/api/users", json={"name": "  Ana  ", "email": "ANA@Example.com"}))
    assert data["name"] == "Ana"
    assert data["email"] == "ana@example.com"


def test_crear_sin_json(client):
    res = client.post("/api/users", data="hola", content_type="text/plain")
    assert res.status_code == 400
    assert body(res)["error"] == "el body debe ser un objeto JSON"


def test_crear_json_malformado(client):
    res = client.post("/api/users", data='{"name":', content_type="application/json")
    assert res.status_code == 400
    assert body(res)["error"] == "el body debe ser un objeto JSON"


def test_crear_json_que_no_es_objeto(client):
    res = client.post("/api/users", json=["Ana"])
    assert res.status_code == 400
    assert body(res)["error"] == "el body debe ser un objeto JSON"


def test_crear_sin_campos(client):
    res = client.post("/api/users", json={})
    assert res.status_code == 400
    assert body(res)["error"] == "name y email son requeridos"


def test_crear_nombre_vacio(client):
    res = client.post("/api/users", json={"name": "  ", "email": "ana@example.com"})
    assert res.status_code == 400
    assert body(res)["error"] == "name debe ser un texto no vacio"


def test_crear_email_invalido(client):
    res = client.post("/api/users", json={"name": "Ana", "email": "ana"})
    assert res.status_code == 400
    assert body(res)["error"] == "email con formato invalido"


def test_email_duplicado(client):
    crear(client)
    res = client.post("/api/users", json={"name": "Otra", "email": "ANA@example.com"})
    assert res.status_code == 409
    assert body(res)["error"] == "email duplicado"


def test_usuario_inexistente(client):
    res = client.get("/api/users/99")
    assert res.status_code == 404
    assert body(res)["error"] == "usuario no encontrado"


def test_actualiza_usuario(client):
    ana = crear(client)
    res = client.put(
        f"/api/users/{ana['id']}",
        json={"name": "Ana Lopez", "email": "ana.lopez@example.com"},
    )
    assert res.status_code == 200
    assert body(res) == {
        "id": ana["id"],
        "name": "Ana Lopez",
        "email": "ana.lopez@example.com",
    }


def test_actualiza_conservando_su_email(client):
    ana = crear(client)
    res = client.put(
        f"/api/users/{ana['id']}",
        json={"name": "Ana Lopez", "email": "ana@example.com"},
    )
    assert res.status_code == 200
    assert body(res)["name"] == "Ana Lopez"


def test_actualizar_inexistente(client):
    res = client.put("/api/users/99", json={"name": "Ana", "email": "ana@example.com"})
    assert res.status_code == 404
    assert body(res)["error"] == "usuario no encontrado"


def test_actualizar_email_de_otro_usuario(client):
    crear(client)
    luis = crear(client, "Luis", "luis@example.com")
    res = client.put(
        f"/api/users/{luis['id']}",
        json={"name": "Luis", "email": "ana@example.com"},
    )
    assert res.status_code == 409
    assert body(res)["error"] == "email duplicado"


def test_actualizar_body_invalido(client):
    ana = crear(client)
    res = client.put(f"/api/users/{ana['id']}", json={"name": "Ana"})
    assert res.status_code == 400
    assert body(res)["error"] == "name y email son requeridos"


def test_elimina_usuario(client):
    ana = crear(client)
    res = client.delete(f"/api/users/{ana['id']}")
    assert res.status_code == 200
    assert body(res) == {"deleted": True, "id": ana["id"]}
    assert client.get(f"/api/users/{ana['id']}").status_code == 404
    assert body(client.get("/api/users")) == []


def test_eliminar_inexistente(client):
    res = client.delete("/api/users/99")
    assert res.status_code == 404
    assert body(res)["error"] == "usuario no encontrado"


def test_ruta_desconocida(client):
    res = client.get("/api/no-existe")
    assert res.status_code == 404
    assert body(res)["error"] == "ruta no encontrada"


def test_metodo_no_permitido(client):
    res = client.post("/api/health")
    assert res.status_code == 405
    assert body(res)["error"] == "metodo no permitido"

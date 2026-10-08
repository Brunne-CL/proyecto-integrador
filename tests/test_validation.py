import pytest

from app.validation import parse_user


def test_usuario_valido_recorta_y_normaliza_email():
    payload, error = parse_user({"name": "  Ana  ", "email": "  Ana@Example.COM "})
    assert error is None
    assert payload == {"name": "Ana", "email": "ana@example.com"}


@pytest.mark.parametrize(
    "data",
    [None, [], "ana", 5],
)
def test_body_que_no_es_objeto(data):
    payload, error = parse_user(data)
    assert payload is None
    assert error == "el body debe ser un objeto JSON"


@pytest.mark.parametrize(
    "data",
    [{}, {"name": "Ana"}, {"email": "ana@example.com"}],
)
def test_faltan_campos(data):
    payload, error = parse_user(data)
    assert payload is None
    assert error == "name y email son requeridos"


@pytest.mark.parametrize(
    "name",
    ["", "   ", None, 12, ["Ana"]],
)
def test_nombre_invalido(name):
    payload, error = parse_user({"name": name, "email": "ana@example.com"})
    assert payload is None
    assert error == "name debe ser un texto no vacio"


def test_nombre_demasiado_largo():
    payload, error = parse_user({"name": "a" * 101, "email": "ana@example.com"})
    assert payload is None
    assert error == "name no puede superar 100 caracteres"


@pytest.mark.parametrize(
    "email",
    [
        None,
        10,
        "",
        "sin-arroba",
        "a@b",
        "@example.com",
        "ana@",
        "ana@.com",
        "ana@example.",
        "ana @example.com",
        "a" * 250 + "@example.com",
    ],
    ids=[
        "null",
        "numero",
        "vacio",
        "sin_arroba",
        "sin_punto",
        "sin_local",
        "sin_dominio",
        "punto_al_inicio",
        "punto_al_final",
        "con_espacio",
        "demasiado_largo",
    ],
)
def test_email_invalido(email):
    payload, error = parse_user({"name": "Ana", "email": email})
    assert payload is None
    assert error == "email con formato invalido"

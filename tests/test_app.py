def test_create_app_toma_la_base_desde_el_entorno(monkeypatch, tmp_path):
    db_path = tmp_path / "desde-env.db"
    monkeypatch.setenv("DB_PATH", str(db_path))

    from app import create_app

    app = create_app()
    assert app.config["DB_PATH"] == str(db_path)
    assert db_path.exists()

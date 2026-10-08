import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app(str(tmp_path / "users.db"))
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client

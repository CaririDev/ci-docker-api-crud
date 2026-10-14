import app as app_module
import pytest

from app import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(app_module, "DATABASE_PATH", tmp_path / "test.db")
    app_module.init_db()
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


def test_index_returns_crud_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Painel CRUD" in response.get_data(as_text=True)


def test_health_check_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "service": "ci-docker-api",
        "status": "ok",
    }


def test_sum_endpoint_returns_result(client):
    response = client.get("/api/soma?a=10&b=5")

    assert response.status_code == 200
    assert response.get_json()["resultado"] == 15


def test_sum_endpoint_rejects_missing_or_invalid_values(client):
    response = client.get("/api/soma?a=dez&b=5")

    assert response.status_code == 400
    assert response.get_json()["error"] == "Informe os parâmetros numéricos a e b."


def test_items_crud(client):
    listed = client.get("/api/items")
    assert listed.status_code == 200
    assert len(listed.get_json()["items"]) == 3

    created = client.post(
        "/api/items",
        json={
            "name": "Escrever documentação",
            "description": "Documentar como executar o projeto.",
            "status": "Pendente",
        },
    )
    assert created.status_code == 201
    item_id = created.get_json()["id"]

    fetched = client.get(f"/api/items/{item_id}")
    assert fetched.status_code == 200
    assert fetched.get_json()["name"] == "Escrever documentação"

    updated = client.put(
        f"/api/items/{item_id}",
        json={"name": "Documentação pronta", "status": "Concluído"},
    )
    assert updated.status_code == 200
    assert updated.get_json()["name"] == "Documentação pronta"
    assert updated.get_json()["description"] == "Documentar como executar o projeto."

    deleted = client.delete(f"/api/items/{item_id}")
    assert deleted.status_code == 204
    assert client.get(f"/api/items/{item_id}").status_code == 404


def test_item_requires_name(client):
    response = client.post("/api/items", json={"description": "Sem nome"})

    assert response.status_code == 400
    assert response.get_json()["error"] == "O nome é obrigatório."


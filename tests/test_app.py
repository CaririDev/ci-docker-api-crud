import app as app_module
import pytest

from app import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(app_module, "DATABASE_PATH", tmp_path / "test.db")
    monkeypatch.setenv("FEATURE_DESCONTO_PROMO", "false")
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


def test_api_status_reports_discount_flag_disabled_by_default(client):
    response = client.get("/api/status")

    assert response.status_code == 200
    assert response.get_json() == {
        "service": "fastorder-api",
        "status": "ok",
        "feature_flags": {"desconto_promo": False},
    }


def test_sum_endpoint_returns_result(client):
    response = client.get("/api/soma?a=10&b=5")

    assert response.status_code == 200
    assert response.get_json()["resultado"] == 15


def test_sum_endpoint_rejects_missing_or_invalid_values(client):
    response = client.get("/api/soma?a=dez&b=5")

    assert response.status_code == 400
    assert response.get_json()["error"] == "Informe os parâmetros numéricos a e b."


def test_discount_endpoint_applies_discount_when_flag_is_enabled(
    client, monkeypatch
):
    monkeypatch.setenv("FEATURE_DESCONTO_PROMO", "true")

    response = client.get("/api/desconto?valor=100")

    assert response.status_code == 200
    assert response.get_json() == {
        "valor_original": 100.0,
        "percentual_desconto": 10,
        "desconto": 10.0,
        "valor_final": 90.0,
    }


def test_discount_endpoint_is_hidden_when_flag_is_disabled(client):
    response = client.get("/api/desconto?valor=100")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Funcionalidade indisponível."}


@pytest.mark.parametrize("value", ["", "abc", "-5", "NaN", "Infinity", "1E100"])
def test_discount_endpoint_rejects_invalid_values(client, monkeypatch, value):
    monkeypatch.setenv("FEATURE_DESCONTO_PROMO", "true")

    response = client.get(f"/api/desconto?valor={value}")

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Informe um valor numérico não negativo."
    }


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
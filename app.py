from datetime import datetime, timezone
from pathlib import Path
import os
import sqlite3

from flask import Flask, jsonify, render_template, request


app = Flask(__name__)
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", "data/items.db"))


def get_db():
    """Abre o banco SQLite e retorna linhas como dicionários."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Cria a tabela e alguns registros iniciais para facilitar o teste."""
    with get_db() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'Pendente',
                created_at TEXT NOT NULL
            )
            """
        )
        count = db.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        if count == 0:
            now = datetime.now(timezone.utc).isoformat()
            db.executemany(
                "INSERT INTO items (name, description, status, created_at) VALUES (?, ?, ?, ?)",
                [
                    ("Configurar pipeline CI", "Executar testes automaticamente a cada push.", "Concluído", now),
                    ("Validar imagem Docker", "Construir e verificar o endpoint de saúde.", "Em andamento", now),
                    ("Publicar no Docker Hub", "Fazer o deploy da imagem quando chegar na branch main.", "Pendente", now),
                ],
            )


def item_to_dict(item):
    return dict(item)


def validate_payload(payload, current=None):
    payload = payload or {}
    name = payload.get("name", current["name"] if current else "")
    description = payload.get(
        "description", current["description"] if current else ""
    )
    status = payload.get("status", current["status"] if current else "Pendente")
    name = str(name).strip()
    description = str(description).strip()
    status = str(status).strip()
    allowed_statuses = {"Pendente", "Em andamento", "Concluído"}

    if not name:
        return None, "O nome é obrigatório."
    if status not in allowed_statuses:
        return None, "Status inválido. Use Pendente, Em andamento ou Concluído."
    return {"name": name, "description": description, "status": status}, None


init_db()


@app.get("/")
def index():
    """Página web para testar o CRUD."""
    return render_template("index.html")


@app.get("/health")
def health():
    """Endpoint usado pelo Docker e pelo pipeline para verificar a aplicação."""
    return jsonify(service="ci-docker-api", status="ok")


@app.get("/api/items")
def list_items():
    with get_db() as db:
        items = db.execute("SELECT * FROM items ORDER BY id DESC").fetchall()
    return jsonify(items=[item_to_dict(item) for item in items])


@app.get("/api/items/<int:item_id>")
def get_item(item_id):
    with get_db() as db:
        item = db.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    if item is None:
        return jsonify(error="Item não encontrado."), 404
    return jsonify(item_to_dict(item))


@app.post("/api/items")
def create_item():
    data, error = validate_payload(request.get_json(silent=True))
    if error:
        return jsonify(error=error), 400

    with get_db() as db:
        cursor = db.execute(
            """
            INSERT INTO items (name, description, status, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                data["name"],
                data["description"],
                data["status"],
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        item = db.execute(
            "SELECT * FROM items WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
    return jsonify(item_to_dict(item)), 201


@app.put("/api/items/<int:item_id>")
def update_item(item_id):
    with get_db() as db:
        current = db.execute(
            "SELECT * FROM items WHERE id = ?", (item_id,)
        ).fetchone()
        if current is None:
            return jsonify(error="Item não encontrado."), 404

        data, error = validate_payload(request.get_json(silent=True), current)
        if error:
            return jsonify(error=error), 400
        db.execute(
            "UPDATE items SET name = ?, description = ?, status = ? WHERE id = ?",
            (data["name"], data["description"], data["status"], item_id),
        )
        item = db.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    return jsonify(item_to_dict(item))


@app.delete("/api/items/<int:item_id>")
def delete_item(item_id):
    with get_db() as db:
        cursor = db.execute("DELETE FROM items WHERE id = ?", (item_id,))
    if cursor.rowcount == 0:
        return jsonify(error="Item não encontrado."), 404
    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)


# Pipeline CI: Integração Contínua, Testes e Deploy com Docker

Exemplo de uma API REST pequena em Flask com CRUD, interface web e pipeline de integração contínua.

## Estrutura

```text
.
├── .github/workflows/ci.yml  # pipeline CI/CD
├── tests/test_app.py         # testes automatizados
├── app.py                    # API Flask
├── templates/index.html      # página web do CRUD
├── static/style.css          # estilos da página
├── static/app.js             # comportamento da página
├── Dockerfile                # imagem de produção
├── docker-compose.yml        # execução local com Docker
├── requirements.txt          # dependências da aplicação
├── requirements-dev.txt      # dependências de desenvolvimento
└── .dockerignore
```

## Executar localmente

Requer Python 3.11+.

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pytest -q
python app.py
```

Depois, acesse `http://localhost:5000/` para abrir o painel CRUD ou `http://localhost:5000/health` para verificar a saúde da API.

## Endpoints CRUD

| Método | Endpoint | Função |
| --- | --- | --- |
| GET | `/api/items` | Lista os itens |
| GET | `/api/items/<id>` | Consulta um item |
| POST | `/api/items` | Cria um item |
| PUT | `/api/items/<id>` | Atualiza um item |
| DELETE | `/api/items/<id>` | Exclui um item |

Os registros são armazenados em SQLite no volume `api_data` do Docker Compose. A página já carrega três itens de exemplo na primeira execução.

## Executar com Docker

```bash
docker compose up --build
```

Teste a aplicação:

```bash
curl http://localhost:5000/health
```

Resposta esperada:

```json
{"service":"ci-docker-api","status":"ok"}
```

## Como funciona o pipeline

O arquivo `.github/workflows/ci.yml` é executado em cada `push` e `pull request`:

1. Instala as dependências e executa os testes com `pytest`.
2. Constrói a imagem Docker.
3. Inicia um container e verifica o endpoint `/health`.
4. Na branch `main`, publica a imagem no Docker Hub quando os secrets `DOCKERHUB_USERNAME` e `DOCKERHUB_TOKEN` estão configurados.

Para configurar o deploy, abra `Settings > Secrets and variables > Actions` no repositório e crie os secrets `DOCKERHUB_USERNAME` e `DOCKERHUB_TOKEN`. A imagem será publicada como `SEU_USUARIO/ci-docker-api` no Docker Hub. Sem esses secrets, os testes e o build continuam funcionando e o deploy é ignorado.


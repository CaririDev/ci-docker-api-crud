# FastOrder API: DevSecOps, Feature Flags e Docker

API Flask com operações CRUD, endpoint de soma, cálculo promocional protegido por feature flag e pipeline DevSecOps no GitHub Actions.

## Executar localmente

Requer Python 3.12 ou superior.

python -m venv .venv
No Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
pytest -v
python app.py

Acesse http://localhost:5000/, http://localhost:5000/health ou http://localhost:5000/api/status.

## Feature flag do desconto

A rota GET /api/desconto?valor=100 concede 10% de desconto somente quando FEATURE_DESCONTO_PROMO=true. O padrão é false; enquanto estiver desativada, a rota responde HTTP 404. O endpoint /api/status informa se a flag está ativa.

Para experimentar no PowerShell, defina $env:FEATURE_DESCONTO_PROMO = "true" antes de executar python app.py.

No Docker Compose, defina a variável no ambiente antes de iniciar ou use um arquivo .env local baseado em .env.example. O arquivo .env é ignorado pelo Git. Ao mudar a configuração do Compose, recrie o contêiner para que ele receba o novo ambiente; a imagem não precisa ser reconstruída.

## Verificações de segurança locais

bandit -r app.py
pip-audit -r requirements.txt

A configuração mantém Bandit e pip-audit em requirements-dev.txt, fora da imagem de produção. O pip-audit verifica as dependências usadas pela aplicação em requirements.txt.

## Docker

docker compose up --build

O Dockerfile atualiza os pacotes do sistema antes da instalação das dependências. A aplicação roda como usuário sem privilégios. Para testar a imagem localmente, execute docker build -t fastorder-api:local . e docker run --rm -p 5000:5000 fastorder-api:local.

## Pipeline DevSecOps

.github/workflows/devsecops-pipeline.yml roda lint e testes, depois executa em sequência:

1. Secret scanning do histórico Git com TruffleHog.
2. SAST do código Python com Bandit.
3. SCA das dependências de produção com pip-audit.

Build e Trivy só começam se os testes e os três scans forem aprovados. A imagem só é publicada no GitHub Container Registry (GHCR) em push para main, após o scan Trivy. O job usa GITHUB_TOKEN; não requer PAT nem credenciais extras. A primeira publicação pode criar o pacote GHCR como privado, então ajuste a visibilidade do pacote em GitHub Packages se a entrega exigir acesso público.
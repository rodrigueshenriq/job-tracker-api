# Job Tracker API

API REST para gerenciamento de candidaturas de emprego, construída com FastAPI e SQLite.

## Visão Geral

O Job Tracker API permite registrar e acompanhar candidaturas a vagas de emprego, com operações completas de CRUD (criar, listar, atualizar e excluir).

**Stack atual:** FastAPI · SQLAlchemy · SQLite · Pydantic  
**Evolução planejada:** migração do armazenamento para [Appwrite TablesDB](https://appwrite.io/docs/products/databases/tables)

## Funcionalidades

- Criar, listar, buscar, atualizar e excluir candidaturas
- Campos: empresa, cargo, status e notas
- Documentação interativa automática via `/docs`
- Configuração via variáveis de ambiente

## Requisitos

- Python 3.10+
- pip

## Instalação

```bash
git clone https://github.com/rodrigueshenriq/job-tracker-api.git
cd job-tracker-api
python -m venv env
# Windows:
.\env\Scripts\activate
# macOS/Linux:
source env/bin/activate
pip install -r requirements.txt
```

## Configuração

Copie o arquivo de exemplo e ajuste conforme necessário:

```bash
cp .env.example .env
```

O `.env` **nunca deve ser versionado**. As variáveis disponíveis são:

```env
DATABASE_URL=sqlite:///./job_tracker.db
APPWRITE_ENDPOINT=https://fra.cloud.appwrite.io/v1
APPWRITE_PROJECT_ID=job-tracker-api
APPWRITE_API_KEY=
```

## Execução

```bash
uvicorn main:app --reload
```

Acesse a documentação em: http://127.0.0.1:8000/docs

## Estrutura do Projeto

```
job-tracker-api/
├── database/
│   └── database.py          # Conexão e sessão SQLAlchemy
├── models/
│   └── models.py            # Modelo JobApplication
├── routers/
│   └── applications.py      # Rotas CRUD de candidaturas
├── schemas/
│   └── schemas.py           # Schemas Pydantic
├── main.py                  # Entrypoint FastAPI
├── requirements.txt         # Dependências
├── .env.example             # Variáveis de ambiente necessárias
└── README.md
```

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/` | Health check |
| POST | `/applications/` | Criar candidatura |
| GET | `/applications/` | Listar candidaturas |
| GET | `/applications/{id}` | Buscar candidatura |
| PUT | `/applications/{id}` | Atualizar candidatura |
| DELETE | `/applications/{id}` | Excluir candidatura |

## Licença

MIT License — veja [LICENSE](LICENSE).

## Créditos

Este projeto evoluiu a partir do [FastAPI-CRUD-Todo](https://github.com/lymanny/FastAPI-CRUD-Todo) de [lymanny](https://lymanny.onrender.com), utilizado como ponto de partida para o domínio de candidaturas.

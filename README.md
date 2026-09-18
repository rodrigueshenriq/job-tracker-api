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

- Python 3.10 ou 3.11 (com as versões atuais de `requirements.txt`)
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
HUMAN_APPROVAL_KEY=
```

## Execução

```bash
uvicorn main:app --reload
```

Acesse a documentação em: http://127.0.0.1:8000/docs

## Testes

Com as dependências de `requirements.txt` instaladas em um ambiente Python 3.10 ou 3.11, execute:

```bash
python -m unittest discover -s tests -v
```

Os testes usam SQLite em memória e não acessam `job_tracker.db`.

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
| GET | `/agent/candidate-profile` | Perfil fictício para demonstração |
| GET | `/agent/application-history` | Histórico fictício para demonstração |
| POST | `/agent/application-results/prepare` | Solicita revisão humana, sem gravar resultado |
| POST | `/agent/application-results/confirm` | Confirmação exclusiva da aplicação/UI humana |

As rotas `/agent` usam apenas dados fixos e fictícios, independentes do banco SQLite real.

### Aprovação humana para resultados

`POST /agent/application-results/prepare` valida um `application_id` de demonstração e um resultado permitido (`interview`, `rejected`, `offer` ou `withdrawn`). Ele cria uma solicitação pendente, devolve um token opaco e o resumo a ser revisado, sem gravar o resultado. A solicitação expira após 10 minutos.

Depois da revisão e aprovação humana, somente a aplicação/UI do operador deve chamar `POST /agent/application-results/confirm` com o token e o cabeçalho `X-Human-Approval-Key`. Configure `HUMAN_APPROVAL_KEY` fora do código e não compartilhe essa credencial com o agente. A confirmação falha se a credencial não estiver configurada ou for inválida; tokens inválidos, expirados ou já usados também falham. Os resultados confirmados ficam apenas na memória do processo de demonstração e se perdem ao reiniciar; as respostas GET fictícias continuam fixas.

A confirmação é a fronteira controlada pela aplicação/UI humana e **não deve ser disponibilizada ao agente como ferramenta**. O OpenAPI padrão da aplicação documenta a rota administrativa; para a futura ferramenta do agente, use somente `build_agent_tool_openapi()` em `agent_tool_openapi.py`. Essa especificação restrita contém os dois GETs e `prepare_application_result`, sem `confirm_application_result` nem as rotas CRUD. Ainda não há integração com Foundry.

## Licença

MIT License — veja [LICENSE](LICENSE).

## Créditos

Este projeto evoluiu a partir do [FastAPI-CRUD-Todo](https://github.com/lymanny/FastAPI-CRUD-Todo) de [lymanny](https://lymanny.onrender.com), utilizado como ponto de partida para o domínio de candidaturas.

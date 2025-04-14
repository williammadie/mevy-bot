# Mevy Bot

## Chatbot V3

### Installation

Download code
```bash
git clone https://github.com/williammadie/mevy-bot.git
cd mevy-bot
```

Deploy stack of development
```bash
cd devstack
docker compose run
```

Access Qdrant dashboard at `http://localhost:6333/dashboard`


Run Mevy Bot Orchestrator
```bash
cd mevy_bot/routers
uv run fastapi dev main.py
```

Access Swagger UI at `http://localhost:8000/docs`

### Developer Installation

> [!NOTE] You need to have [uv package manager](https://docs.astral.sh/uv/) installed locally before proceeding.

Download code
```bash
git clone https://github.com/williammadie/mevy-bot.git
cd mevy-bot
```

Install Python dependencies
```bash
uv sync
```

Run Mevy Bot Orchestrator
```bash
cd mevy_bot/routers
uv run fastapi dev main.py
```

Access Swagger UI at `http://localhost:8000/docs`

## Miscellaneous Commands

Run RAG tests
```bash
deepeval test run tests/retriever/test_retriever.py
```

## Chatbot V2 (n8n version)

### Installation

Download code
```bash
git clone https://github.com/williammadie/mevy-bot.git
cd mevy-bot
```

Deploy stack of development
```bash
cd n8n-sandbox
docker compose run
```

### Useful links

|    **Component**   |   **Access Information**   |                          **Credentials**                         |
|:------------------:|:--------------------------:|:----------------------------------------------------------------:|
|         n8n        |    http://localhost:5678   |               Create an account on first connexion               |
| Legifrance Service | http://localhost:8000/docs |                           No auth (WIP)                          |
|      pgVector      |    http://localhost:5432   |             username `postgres`, password `postgres`             |
|      pgAdmin4      |    http://localhost:8888   | username `user-name@domain-name.com`, password `strong-password` |
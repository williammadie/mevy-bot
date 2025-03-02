# Mevy Bot

## Installation

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

Run bot commands (see section blow)

## Bot commands

See available actions
```bash
python3 -m mevy_bot -h
```

Chat through the GUI
```bash
cd mevy_bot/
streamlit run app.py
```

## Miscellaneous Commands

Run RAG tests
```bash
deepeval test run tests/retriever/test_retriever.py
```
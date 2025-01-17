# chatbot_backend2

## Requirements
- Ollama running at http://localhost:11434/

## Development Setup
- Create and activate a python virtual environment of your choice
```shell
python -m venv .venv
./.venv/Scripts/Activate.ps1
```
- Install packages
```shell
pip install -r requirements.txt
```

- Run development server:
```
python src/main.py
```

Server is accessible from `http://localhost:5000/`

## API Documentation

### Content Routes

#### POST /content
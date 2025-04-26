# Tango

Um projeto de assistente virtual com capacidade de processamento de linguagem natural e base de conhecimento vetorial.

## Estrutura do Projeto

- **frontend**: Interface com React/TypeScript
- **backend**: API FastAPI com processamento de linguagem natural

## Requisitos

### Frontend
- Node.js 18+
- npm ou yarn

### Backend
- Python 3.10+
- pip

## Como Executar

### Backend

```bash
cd backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Iniciar o servidor
python main.py
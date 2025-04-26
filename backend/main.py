from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints import assistant

app = FastAPI(
    title="Mango ",
    description="API para assistente virtual",
    version="0.1.0"
)

# Configuração de CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adiciona os endpoints da assistente
app.include_router(assistant.router, prefix="/api/assistant", tags=["assistant"])

# Rota de teste
@app.get("/")
async def root():
    return {"message": "Bem-vindo à API da Assistente"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
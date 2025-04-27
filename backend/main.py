from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.api import router as api_router

app = FastAPI(
    title="Mango API",
    description="API para o assistente virtual",
    version="0.1.0"
)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui as rotas da API
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Bem-vindo à API do Tango! Acesse /docs para a documentação."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
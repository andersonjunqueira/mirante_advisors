from fastapi import FastAPI

from app.database import Base, engine
from app.routes import router

app = FastAPI()

# Cria tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Registra rotas
app.include_router(router)

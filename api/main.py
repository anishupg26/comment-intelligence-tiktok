from fastapi import FastAPI
from api.routes import router

app = FastAPI(title="AI Creator Comment Intelligence API")

app.include_router(router)

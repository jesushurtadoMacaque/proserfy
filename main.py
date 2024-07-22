from fastapi import FastAPI
import models.user as models
from config.database import engine, init_db
from fastapi.middleware.cors import CORSMiddleware
from routes import users
import uvicorn
import os
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


init_db()

models.Base.metadata.create_all(bind=engine)

app.include_router(users.router)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)


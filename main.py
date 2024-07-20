from fastapi import FastAPI
import models.user as models
from config.database import engine, init_db
from routes import users
app = FastAPI()

init_db()

models.Base.metadata.create_all(bind=engine)

app.include_router(users.router)


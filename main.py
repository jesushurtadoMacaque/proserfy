from fastapi import FastAPI
import models.user as models
from config.database import engine, init_db
from routes import users
import os
app = FastAPI()

init_db()

models.Base.metadata.create_all(bind=engine)

app.include_router(users.router)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)


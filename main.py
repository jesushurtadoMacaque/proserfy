from utils.error_handler import generic_error_exception_handler, validation_exception_handler
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from custom_exceptions.users_exceptions import GenericException
import models.user as models
from config.database import engine, init_db
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routes import users
import uvicorn
import os


load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.add_exception_handler(GenericException, generic_error_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

init_db()

models.Base.metadata.create_all(bind=engine)

app.include_router(users.router)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)


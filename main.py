from fastapi.staticfiles import StaticFiles
import config.database
import config.files
from utils.error_handler import generic_error_exception_handler, validation_exception_handler
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from custom_exceptions.users_exceptions import GenericException
import models.users as models
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routes import user, professional_service
import uvicorn
import os
import config

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

app.mount("/uploaded_images/services", StaticFiles(directory=config.files.UPLOAD_DIRECTORY), name="uploaded_images")


config.database.init_db()

models.Base.metadata.create_all(bind=config.database.engine)

app.include_router(user.router, prefix="/v1")
app.include_router(professional_service.router, prefix="/v1")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)


from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from custom_exceptions.users_esceptions import GenericException
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


@app.exception_handler(GenericException)
async def item_not_found_exception_handler(request: Request, exc: GenericException):
    return JSONResponse(
        status_code=exc.code,
        content={"error": f"{exc.message}"},
    )

init_db()

models.Base.metadata.create_all(bind=engine)

app.include_router(users.router)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)


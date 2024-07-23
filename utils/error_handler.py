from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from custom_exceptions.users_exceptions import GenericException

async def generic_error_exception_handler(request: Request, exc: GenericException):
    return JSONResponse(
        status_code=exc.code,
        content={"error": f"{exc.message}"},
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": exc.errors()[0]["msg"]}
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_messages = []

    for error in errors:
        field_name = error["loc"][-1]  # Tomamos solo el último elemento que es el nombre del campo
        error_message = f"{field_name}: {error['msg']}"
        error_messages.append(error_message)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"errors": error_messages}
    )

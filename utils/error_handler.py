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
    errors = exc.errors()
    error_messages = []

    for error in errors:
        field_name = error["loc"][-1] # Last error
        error_message = f"{field_name}: {error['msg']}"
        error_messages.append(error_message)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"errors": error_messages}
    )


# Define a standard response for validation errors
validation_error_response = {
    422: {
        "description": "Validation Error",
        "content": {
            "application/json": {
                "example": {"errors": ["field_name: error message"]}
            }
        },
    },
    401: {
        "description": "Unauthorized",
        "content": {
            "application/json": {
                "example": {"error": "Invalid authentication credentials"}
            }
        },
    },
    404: {
        "description": "Not Found",
        "content": {
            "application/json": {
                "example": {"error": "field_name not found"}
            }
        },
    },
    500: {
        "description": "Server error",
        "content": {
            "application/json": {
                "example": {"error": "Server error"}
            }
        },
    },
}
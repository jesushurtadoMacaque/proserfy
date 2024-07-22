class GenericException(Exception):
    def __init__(self, message: str, code: int):
        self.message = message
        self.code = code

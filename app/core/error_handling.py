class CustomError(Exception):
    def __init__(self, code: int, message: str, resolution: str):
        self.code = code
        self.message = message
        self.resolution = resolution
        super().__init__(self.message)

    def __str__(self):
        return f"[{self.code}] {self.message} - {self.resolution}"


class NotFoundError(CustomError):
    def __init__(self):
        super().__init__(404, "Resource not found.", "Check the resource identifier and try again.")


class ValidationError(CustomError):
    def __init__(self):
        super().__init__(400, "Validation failed.", "Ensure all required fields are correctly filled.")


class ServerError(CustomError):
    def __init__(self):
        super().__init__(500, "Internal server error.", "Please contact support.")

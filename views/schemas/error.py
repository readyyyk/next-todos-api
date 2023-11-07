from pydantic import BaseModel


class ErrorSchema(BaseModel):
    message: str | None = None
    code: int | None = None

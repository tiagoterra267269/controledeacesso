from pydantic import BaseModel

class LoginSchema(BaseModel):
    login: str = "login",
    senha: str = "senha"

class LoginSchemaResponse(BaseModel):
    login: str = "login",
    token: str = "token"
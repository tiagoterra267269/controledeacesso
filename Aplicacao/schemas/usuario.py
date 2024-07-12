from typing import Optional, List
from model.entidades import Usuario
from pydantic import BaseModel
from datetime import datetime

class SearchUsuarioSchema(BaseModel):
    usuarioId: int = 1 

class ExcluirSchema(BaseModel):
    usuarioId: int = 1

class UsuarioSchema(BaseModel):
    """ Define um novo Usuario a ser inserido na base
    """
    usuarioid: int = 1
    login: str = "Jonh Doe"
    senha: str = "jondoe@email.com"
    perfis: List[int] = [1, 2, 3]
    ativo: int = 1

class UsuarioViewSchema(BaseModel):
    """ Define o Usuario retornado
    """
    login: str = "Jonh Doe"
    senha: str = "jondoe@email.com"
    usuarioid: int = 1
    ativo: int = 1

class ListagemUsuariosSchema(BaseModel):
    """ Define como uma listagem de Usuarios será retornada.
    """
    usuarios:List[UsuarioViewSchema]

def mapeaentidade_paraschemaUsuarios(usuarios: List[Usuario]):
    """ Mapea uma lista de entidade Usuario para lista de UsuariosSchema

    Retorna uma lista de UsuariosSchema
    """
    result = []
    for usuario in usuarios:
        result.append({
            "login": usuario.login,
            "senha": usuario.senha,
            "ativo": usuario.ativo,
            "id": usuario.usuarioid
        })

    return {"Usuarios": result}

def mapeaentidade_paraschemaUsuario(usuario: Usuario):
    """ Mapea uma entidade Usuario para UsuarioSchema

    Retorna um UsuarioSchema
    """
    return {
        "login": usuario.login,
        "usuarioid" :usuario.usuarioid
    }
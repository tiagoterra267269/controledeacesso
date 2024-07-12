from typing import Optional, List
from model.entidades import Perfil
from pydantic import BaseModel
from datetime import datetime

class PerfilViewSchema(BaseModel):
    """ Define o Perfil retornado
    """
    id: int = 1
    nome: str = "Perfil 1"

class ListagemPerfilsSchema(BaseModel):
    """ Define como uma listagem de Perfils será retornada.
    """
    Perfils:List[PerfilViewSchema]

def mapeaentidade_paraschemaPerfil(Perfils: List[Perfil]):
    """ Mapea uma lista de entidade Perfil para umalista de PerfilsSchema

    Retorna uma lista de PerfilsSchema
    """
    result = []
    for Perfil in Perfils:
        result.append({
            "nome": Perfil.nome,
            "id": Perfil.id
        })

    return {"Perfils": result}

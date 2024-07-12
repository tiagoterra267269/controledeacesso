from typing import Optional, List
from model.entidades import Aplicacao
from pydantic import BaseModel
from datetime import datetime

class SearchAplicacaoSchema(BaseModel):
    aplicacaoid: int = 1 

class ExcluirSchema(BaseModel):
    aplicacaoid: int = 1

class AplicacaoSchema(BaseModel):
    """ Define um novo Aplicacao a ser inserido na base
    """
    aplicacaoid: int = 1
    nome: str = "Eventos"
    ativo: int = 1

class AplicacaoViewSchema(BaseModel):
    """ Define o Aplicacao retornado
    """
    aplicacaoid: int = 1
    nome: str = "Eventos"
    ativo: int = 1

class ListagemAplicacaosSchema(BaseModel):
    """ Define como uma listagem de Aplicacaos será retornada.
    """
    aplicacaos:List[AplicacaoViewSchema]

def mapeaentidade_paraschemaAplicacaos(aplicacaos: List[Aplicacao]):
    """ Mapea uma lista de entidade Aplicacao para lista de AplicacaosSchema

    Retorna uma lista de AplicacaosSchema
    """
    result = []
    for aplicacao in aplicacaos:
        result.append({
            "nome": aplicacao.nome,
            "ativo": aplicacao.ativo,
            "aplicacaoid": aplicacao.aplicacaoid
        })

    return {"aplicacaos": result}

def mapeaentidade_paraschemaAplicacao(aplicacao: Aplicacao):
    """ Mapea uma entidade Aplicacao para AplicacaoSchema

    Retorna um AplicacaoSchema
    """
    return {
        "nome": aplicacao.nome,
        "ativo": aplicacao.ativo,
        "aplicacaoid": aplicacao.aplicacaoid
    }
from sqlalchemy import Column, Integer, String, DateTime, LargeBinary, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Union

Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuario'

    usuarioid = Column(Integer, primary_key=True)
    login = Column(String)
    senha = Column(String)
    ativo =  Column(Integer)
    salt = Column(LargeBinary)

    perfis = relationship(
        "Perfil", 
        secondary="perfilusuario",
        back_populates="usuarios")

    def __init__(self, login:str, senha:str, salt:bytes):
        self.login = login
        self.senha = senha
        self.ativo = 1
        self.salt = salt

class Perfil(Base):
    __tablename__ = 'perfil'

    perfilid = Column(Integer, primary_key=True)
    nome = Column(String)
    ativo =  Column(Integer)

    usuarios = relationship(
        "Usuario", 
        secondary="perfilusuario",
        back_populates="perfis"
    )

    def __init__(self, nome:str):
        self.nome = nome
        self.ativo = 1

class Aplicacao(Base):
    __tablename__ = 'Aplicacao'

    aplicacaoid = Column(Integer, primary_key=True)
    nome = Column(String)
    ativo = Column(Integer)

perfilusuario = Table(
    'perfil_usuario', 
    Base.metadata,
    Column('UsuarioId', Integer, ForeignKey(Usuario.usuarioid)),
    Column('PerfilId', Integer, ForeignKey(Perfil.perfilid))
)

Usuario.perfis = relationship(
    Perfil, 
    secondary=perfilusuario, 
    back_populates="usuarios"
)

Perfil.usuarios = relationship(
    Usuario,
    secondary=perfilusuario,
    back_populates="perfis"
)
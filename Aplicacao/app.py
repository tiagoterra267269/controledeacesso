import re
import bcrypt
import logging
from datetime import datetime, timedelta
import jwt
import jsonify

from schemas import *
from flask_cors import CORS
from datetime import datetime
from urllib.parse import unquote
from typing import Optional, List
from flask import redirect, request
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine, func
from flask_openapi3 import OpenAPI, Info, Tag
from model import Session, Usuario, Aplicacao#, Perfil
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import create_engine, Table, MetaData, select 
# from schemas import UsuarioSchema, UsuarioSchema, ExcluirSchema, ListagemUsuariosSchema, SearchUsuarioSchema

# ========================================================================================================
# Configura log
# ========================================================================================================
logging.basicConfig(filename='controledeacesso.log', encoding='utf-8', level=logging.DEBUG)

# ========================================================================================================
# Controle de Acesso
# ========================================================================================================
info = Info(title="Controle de Acesso API", version="1.0.0",
    description="Serviço que permite a manutenção de eventos (workshops, encontros de estudo)")
app = OpenAPI(__name__, info=info)

CORS(app)
app.config['SECRET_KEY'] = 'your_secret_key'

# ========================================================================================================
# Tags
# ========================================================================================================
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")

usuario_tag = Tag(name="Responsável", description="""Endpoints de suporte à responsável: os resposáveis
    presidirão os centros de intersse do evento nos quais os participantes vão dedicir de associam ou não.
    """)

aplicacao_tag = Tag(name="Aplicação", description="""Endpoints referentes às aplicações cadasradas.""")

login_tag = Tag(name="Login", description="""Endpoints referentes a acesso.""")

# ========================================================================================================
# Endpoints de responsáveis 
# ========================================================================================================
@app.post('/usuario', tags=[usuario_tag],responses={"200": UsuarioViewSchema, "409": 
    ErrorSchema, "400": ErrorSchema})
def add_usuario(form: UsuarioSchema):
    """Adiciona um novo usuario à base de dados
    Retorna o responsável adicionado
    """    
    try:
        logging.debug(f"Adicionando usuario de login: '{form.login}'")
        # criando conexão com a base
        session = Session()

        if (form.login == None):
            return {"message": "Login é obrigatório"}, 400
        elif session.query(Usuario).filter(
            Usuario.login == form.login, 
            Usuario.ativo == 1).first() != None:
            return {"message": "Já existe um usuário cadastrado com esse login!"}, 400

        regex = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'

        if (form.senha == None):
            return {"message": "Senha é obrigatório"}, 400
        elif not (re.match(regex, form.senha)):
            return {"message": "Senha inválida"}, 400

        salt = bcrypt.gensalt()
        senha = gerar_hash_senha(form.senha, salt)

        usuario = Usuario(
            login=form.login,
            senha=senha,
            salt=salt)

        # adicionando usuario
        session.add(usuario)
        # efetivando o comando de adição de novo item na tabela
        session.commit()

        logging.debug(f"Adicionado usuario de nome: '{usuario.login}'")

        return mapeaentidade_paraschemaUsuario(usuario), 200

    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        logging.warning(e)
        error_msg = "usuario de mesmo nome já salvo na base :/"
        logging.warning(f"Erro ao adicionar usuario '{usuario.login}', {error_msg}")
        return {"message": error_msg}, 409
    except Exception as e:
        # caso um erro fora do previsto
        logging.warning(e)
        error_msg = "Não foi possível salvar novo item :/"
        logging.warning(f"Erro ao adicionar usuario '{usuario.login}', {error_msg}")
        return {"message": error_msg}, 400

@app.get('/usuario', tags=[usuario_tag], responses={"200": ListagemUsuariosSchema, "404": ErrorSchema})
def get_usuario(query: SearchUsuarioSchema):
    """ Obtém todos os responsáveis de acordo com o evento
    Retorna uma lista de responsáveis de um evento
    """    
    try:
        session = Session()

        logging.debug("Consulta todos os usuarios")
        
        # obtém os responsáveis válidos
        usuariosvalidos = session.query(Usuario).filter(
            Usuario.usuarioid == query.usuarioId, Usuario.ativo == 1).first()
        
        return mapeaentidade_paraschemaUsuario(usuariosvalidos), 200

    except Exception as e:
        # caso um erro fora do previsto
        logging.warning(f"Erro ao consultar os usuarios {e}")
        return {"message : Erro ao consultar os usuarios"}, 500

@app.delete('/usuario', tags=[usuario_tag],responses={"200": UsuarioViewSchema, "409": 
    ErrorSchema, "400": ErrorSchema})
def delete_usuario(form: ExcluirSchema):
    """Remove usuario na base de dados
    Retorna o usuario excluído
    """    
    try:
        logging.debug(f"Excluindo usuário de id: '{form.usuarioId}'")
        # criando conexão com a base
        session = Session()

        # obtém responsável para exclusão
        usuarioparaexclusao = session.query(Usuario).filter(
            Usuario.usuarioid == form.usuarioId, 
            Usuario.ativo == 1).first()
        
        logging.debug(f"Obtem usuario para exclusão : '{form.usuarioId}'")
        
        if (usuarioparaexclusao == None):
            return {"message": "Usuário não encontrado!"}, 400

        # exclui o usuario: nossa exclusao é lógica para garantir rastreabilidade
        usuarioparaexclusao.ativo = 0

        # efetivando o comando de adição de novo item na tabela
        session.commit()

        return mapeaentidade_paraschemaUsuario(usuarioparaexclusao), 200

    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        logging.warning(e)
        logging.warning(f"Erro ao excluir usuario '{usuario.login}', {e}")
        return {"message": error_msg}, 409
    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível excluir o item :/"
        logging.warning(f"Erro ao excluir usuario '{usuario.login}', {e}")
        return {"message": error_msg}, 400

def gerar_hash_senha(senha, salt):
    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), salt)
    return senha_hash

def verificar_senha(senha, senha_hash):
    return bcrypt.checkpw(senha.encode('utf-8'), senha_hash)
    # return bcrypt.checkpw(senha.decode('utf-8'), senha_hash)


# ========================================================================================================
# Endpoints de Aplicação
# ========================================================================================================
@app.get('/aplicacao', tags=[aplicacao_tag], responses={"200": ListagemAplicacaosSchema, "404": ErrorSchema})
def get_aplicacoes():
    """ Obtém todos as aplicações ativas
    """    
    try:
        session = Session()

        logging.debug("Consulta todas as aplicações")
        
        # obtém os responsáveis válidos
        aplicacoesValidas = session.query(Aplicacao).filter(
            Aplicacao.ativo == 1)

        logging.debug(aplicacoesValidas.count())
        
        return mapeaentidade_paraschemaAplicacaos(aplicacoesValidas), 200

    except Exception as e:
        # caso um erro fora do previsto
        logging.warning(f"Erro ao consultar as aplicações {e}")
        return {"message : Erro ao consultar as aplicações"}, 500

# ========================================================================================================
# Endpoints de Login
# ========================================================================================================
@app.post('/login', tags=[login_tag], responses={"200": LoginSchemaResponse, "404": ErrorSchema})
def login(form: LoginSchema):

    try:

        logging.debug("Inicializa login")

        if form.login == None:
            return {"message": "Login é obrigatório!"}, 400
        elif form.senha == None: 
            return {"message": "Senha é obrigatória!"}, 400

        session = Session()

        logging.debug("Abriu sessão")

        usuarioLogado = session.query(Usuario).filter(
            Usuario.login == form.login, Usuario.ativo == 1).first()

        logging.debug("consultou usuario")

        if usuarioLogado == None:
            return {"message": "Usuário não encontrado!"}, 400
        if not verificar_senha(form.senha, usuarioLogado.senha):
            return {"message": "Senha inválida!"}, 400

        logging.debug("vai pro jwt encode")

        token = jwt.encode({
            'id': usuarioLogado.usuarioid,
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        logging.debug("retornando o encode")

        return {'token': token}, 200

    except Exception as e:
        # caso um erro fora do previsto
        logging.warning(f"Erro ao logar {e}")
        return {"message": e}, 500

def token_required(f):
    def wrap(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return {'message': 'Token is missing'}, 403

        try:
            token = token.replace("Bearer ","")

            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return {'message': 'Token has expired'}, 403
        except jwt.InvalidTokenError as e:
            logging.debug('exception')
            logging.debug(e)
            return {'message': 'Token is invalid'}, 403

        return f(*args, **kwargs)

    wrap.__name__ = f.__name__
    return wrap

@app.get('/checks', tags=[aplicacao_tag], responses={"200": ListagemAplicacaosSchema, "404": ErrorSchema})
@token_required
def get_evento():
    return {'passou': 'pasou'}, 200


# if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
"""Conexão local; a inicialização não cria nem altera tabelas."""
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env', override=False)


class DatabaseConfigurationError(Exception):
    """Configuração incompleta, apresentada ao usuário sem expor credenciais."""


@lru_cache
def get_engine():
    password = os.getenv('DB_PASSWORD')
    if password is None or password == 'PREENCHA_COM_A_SENHA_LOCAL':
        raise DatabaseConfigurationError('Configure DB_PASSWORD no arquivo .env.')
    try:
        port = int(os.getenv('DB_PORT', '3306'))
        if not 1 <= port <= 65535:
            raise ValueError
    except ValueError as error:
        raise DatabaseConfigurationError('Porta inválida.') from error
    # URL.create preserva senhas que contenham @, #, espaços ou outros símbolos.
    url = URL.create(
        'mysql+pymysql', username=os.getenv('DB_USER', 'root'), password=password,
        host=os.getenv('DB_HOST', 'localhost'), port=port,
        database=os.getenv('DB_NAME', 'escola_hello_kitty'), query={'charset': 'utf8mb4'},
    )
    return create_engine(url, pool_pre_ping=True, pool_recycle=1800,
                         connect_args={'connect_timeout': 5}, hide_parameters=True)


def get_session():
    # Uma sessão por requisição; o fechamento desfaz transações não confirmadas.
    with Session(get_engine(), expire_on_commit=False) as session:
        yield session

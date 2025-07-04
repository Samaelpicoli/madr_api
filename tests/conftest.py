from contextlib import contextmanager
from datetime import datetime

import factory
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from madr.app import app
from madr.database.get_session import get_session
from madr.models.account import Account, table_registry
from madr.security.password_check import get_password_hash
from madr.settings.settings import Settings


class AccountFactory(factory.Factory):
    """
    Fábrica para criar instâncias de Accounts para testes.
    Esta fábrica utiliza a biblioteca `factory_boy` para gerar
    instâncias de Account com dados aleatórios. Os campos
    'username', 'email' e 'password' são preenchidos com valores
    gerados aleatoriamente.

    Attributes:
        username (factory.Sequence): Gera um nome de usuário único, o sequence,
        é incrementado a cada chamada, garantindo que cada usuário tenha
        um nome de usuário exclusivo.

        email (factory.LazyAttribute): Gera um email baseado no nome de
        usuáro, o lazy significa que o email é gerado após atributos que
        não são fixos serem definidos, garantindo que o email
        seja sempre único e relacionado ao nome de usuário.

        password (factory.LazyAttribute): Gera uma senha baseada no nome
        de usuário, garantindo que a senha seja sempre única e relacionada
        ao nome de usuário. A senha é gerada após os atributos que não são
        fixos serem definidos, garantindo que a senha seja sempre
        consistente com o nome de usuário.
    """

    class Meta:
        """
        Meta class para definir o modelo associado à fábrica.
        """

        model = Account

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')


@pytest.fixture
def client(session):
    """
    Cria um cliente de teste para a aplicação FastAPI.
    Esta função cria um cliente de teste que pode ser usado para
    fazer requisições à aplicação durante os testes. A função
    substitui a dependência de sessão do banco de dados pela
    sessão de teste fornecida. Após os testes, a dependência
    é restaurada.

    Args:
        session (Session): A sessão de banco de dados para os testes.

    Yields:
        TestClient: Um cliente de teste configurado para a aplicação.
    """

    def get_session_override():
        """
        Substitui a dependência de sessão do banco de dados pela
        sessão de teste fornecida.
        Esta função é usada para garantir que a sessão de teste
        seja usada durante os testes, em vez da sessão padrão
        definida na aplicação.

        Returns:
            Session: A sessão de banco de dados para os testes.
        """
        return session

    with TestClient(app) as test_client:
        app.dependency_overrides[get_session] = get_session_override
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
def engine():
    """
    Cria um motor de banco de dados assíncrono para testes.
    Esta função cria um motor de banco de dados assíncrono usando o
    SQLAlchemy e o URL de conexão do banco de dados fornecido pelo
    PostgresContainer. O motor é usado para interagir com o banco de dados
    durante os testes. O escopo da fixture é definido como 'session', o que
    significa que o motor será criado uma vez por sessão de teste e
    será compartilhado entre todos os testes. Isso melhora a eficiência
    dos testes, evitando a criação repetida do motor para cada teste.

    Yields:
        AsyncEngine: Um motor de banco de dados assíncrono configurado
        para os testes. O motor é usado para criar sessões de banco de dados
        e executar operações de banco de dados durante os testes.
    """
    with PostgresContainer('postgres:17', driver='psycopg') as postgres:
        yield create_async_engine(postgres.get_connection_url())


@pytest_asyncio.fixture
async def session(engine):
    """
    Cria uma sessão de banco de dados para testes.
    Esta função cria uma sessão de banco de dados assíncrona usando o
    motor de banco de dados fornecido. A sessão é usada para
    interagir com o banco de dados durante os testes. A sessão é
    gerenciada de forma assíncrona para permitir operações não bloqueantes.

    Yields:
        AsyncSession: Uma sessão de banco de dados assíncrona configurada
        para os testes. A sessão é usada para realizar operações de banco
        de dados durante os testes, como inserção, atualização e consulta
        de dados. A sessão é fechada automaticamente após o uso, garantindo
        que os recursos sejam liberados corretamente.
    """

    async with engine.begin() as conn:
        # Cria todas as tabelas definidas no modelo
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        # Limpa o banco de dados antes de cada teste
        yield session

    async with engine.begin() as conn:
        # Destrói todas as tabelas após os testes
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def account(session: AsyncSession):
    """
    Cria um usuário de teste no banco de dados.
    Esta função cria um usuário com nome de usuário, email e senha
    fornecidos. O usuário é adicionado à sessão do banco de dados
    e a sessão é confirmada. Após a confirmação, o usuário é
    recuperado e retornado.

    Args:
        session (Session): A sessão de banco de dados para os testes.

    Returns:
        Account: O usuário criado no banco de dados.
    """
    password = 'testpassword'
    account = Account(
        username='testuser',
        email='test@test.com',
        password=get_password_hash(password),
    )
    session.add(account)
    await session.commit()
    await session.refresh(account)

    account.clean_password = password

    return account


@pytest_asyncio.fixture
async def other_account(session: AsyncSession):
    """
    Cria uma nova conta de usuário de teste no banco de dados.
    Esta função utiliza o AccountFactory, para facilitar a criação dos dados.
    O usuário é adicionado à sessão do banco de dados
    e a sessão é confirmada. Após a confirmação, o usuário é
    recuperado e retornado.

    Args:
        session (Session): A sessão de banco de dados para os testes.

    Returns:
        Account: O usuário criado no banco de dados.
    """
    password = 'testpassword'
    account = AccountFactory(password=get_password_hash(password))
    session.add(account)
    await session.commit()
    await session.refresh(account)

    account.clean_password = password

    return account


@contextmanager
def _mock_db_time(model, time=datetime(2025, 5, 20)):
    """
    Gerencia um contexto para simular o tempo em um modelo SQLAlchemy.
    Esta função é um gerenciador de contexto que substitui o valor
    do campo 'created_at' do modelo especificado pelo valor de tempo
    fornecido. O valor padrão é 20 de maio de 2025. Após o uso, o
    gerenciador de contexto remove o evento que foi adicionado.

    Args:
        model: O modelo SQLAlchemy que contém o campo 'created_at'.
        time (datetime, opcional): O valor de tempo a ser simulado.
        O padrão é 20 de maio de 2025.

    Yields:
        datetime: O valor de tempo simulado.
    """

    def fake_time_hook(mapper, connection, target):
        """
        Função de gancho que substitui o valor do campo 'created_at'
        do modelo pelo valor de tempo fornecido.

        Args:
            mapper: O mapeador SQLAlchemy.
            connection: A conexão com o banco de dados.
            target: O objeto alvo que está sendo inserido.
        """
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    """
    Fixture que fornece um gerenciador de contexto para simular o
    tempo em um modelo SQLAlchemy. O valor padrão é 20 de maio de
    2025. Esta fixture pode ser usada em testes para garantir que
    o campo 'created_at' do modelo tenha um valor específico.

    Returns:
        _mock_db_time: O gerenciador de contexto que simula o tempo.
    """
    return _mock_db_time


@pytest.fixture
def token(client, account):
    """
    Gera um token JWT de autenticação para o usuário de teste.

    Esta fixture faz uma requisição POST para a rota /token usando
    as credenciais do usuário de teste e retorna o token de acesso
    gerado.

    Args:
        client (TestClient): Cliente de teste.
        account (Account): Usuário de teste criado pela fixture account.

    Returns:
        str: Token JWT de acesso para autenticação.
    """
    response = client.post(
        '/auth/token',
        data={'username': account.email, 'password': account.clean_password},
    )

    return response.json()['access_token']


@pytest.fixture
def settings():
    return Settings()

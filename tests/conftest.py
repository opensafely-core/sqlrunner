import pytest

from .databases import make_mssql_database
from .docker import Containers


@pytest.fixture(scope="session")
def containers():
    yield Containers()


@pytest.fixture(scope="session")
def mssql_database(containers):
    database = make_mssql_database(containers)
    yield database

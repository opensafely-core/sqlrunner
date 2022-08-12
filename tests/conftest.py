import pytest

from .databases import make_mssql_database, wait_for_database
from .docker import Containers


@pytest.fixture(scope="session")
def containers():
    yield Containers()


@pytest.fixture(scope="session")
def mssql_database(containers):
    database = make_mssql_database(containers)
    wait_for_database(database)
    yield database

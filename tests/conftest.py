import pytest
import structlog
from structlog.testing import LogCapture

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


@pytest.fixture
def dsn(mssql_database):
    dialect = "mssql"
    driver = "pymssql"
    user = mssql_database["username"]
    password = mssql_database["password"]
    server = mssql_database["host_from_host"]
    port = mssql_database["port_from_host"]
    database = mssql_database["db_name"]
    dsn = f"{dialect}+{driver}://{user}:{password}@{server}:{port}/{database}"
    return dsn


@pytest.fixture
def log_output():
    return LogCapture()


@pytest.fixture(autouse=True)
def configure_structlog(log_output):
    structlog.configure(processors=[log_output])

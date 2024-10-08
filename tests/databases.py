import time
from pathlib import Path

import pymssql


MSSQL_SETUP_DIR = Path(__file__).absolute().parent / "support/mssql"


def wait_for_database(database, timeout=10):
    start = time.time()
    limit = start + timeout
    while True:
        try:
            conn = pymssql.connect(
                user=database["username"],
                password=database["password"],
                server=database["host_from_host"],
                port=database["port_from_host"],
                database=database["db_name"],
            )
            cursor = conn.cursor()
            cursor.execute("SELECT 'hello'")
            conn.close()
            break
        except pymssql.OperationalError as e:  # pragma: no cover
            if time.time() > limit:
                raise Exception(
                    f"Failed to connect to database after {timeout} seconds"
                ) from e
            time.sleep(1)


def make_mssql_database(containers):
    container_name = "sqlrunner-mssql"
    password = "Your_password123!"
    mssql_port = 1433

    if not containers.is_running(container_name):  # pragma: no cover
        run_mssql(container_name, containers, password, mssql_port)

    container_ip = containers.get_container_ip(container_name)
    host_mssql_port = containers.get_mapped_port_for_host(container_name, mssql_port)

    return {
        "protocol": "mssql",
        "driver": "pymssql",
        "host_from_container": container_ip,
        "port_from_container": mssql_port,
        "host_from_host": "localhost",
        "port_from_host": host_mssql_port,
        "username": "SA",
        "password": password,
        "db_name": "test",
    }


def run_mssql(container_name, containers, password, mssql_port):  # pragma: no cover
    containers.run_bg(
        name=container_name,
        # This is *not* the version that TPP run for us in production which, as of
        # 2024-09-24, is SQL Server 2016 (13.0.5893.48). That version is not available
        # as a Docker image, so we run the oldest supported version instead. Both the
        # production server and our test server set the "compatibility level" to the
        # same value so the same feature set should be supported.
        image="mcr.microsoft.com/mssql/server:2019-CU28-ubuntu-20.04",
        volumes={
            MSSQL_SETUP_DIR: {"bind": "/mssql", "mode": "ro"},
        },
        # Choose an arbitrary free port to publish the MSSQL port on
        ports={mssql_port: None},
        environment={
            "SA_PASSWORD": password,
            "ACCEPT_EULA": "Y",
            "MSSQL_TCP_PORT": str(mssql_port),
        },
        entrypoint="/mssql/entrypoint.sh",
        command="/opt/mssql/bin/sqlservr",
    )

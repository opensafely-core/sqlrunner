from pathlib import Path


MSSQL_SETUP_DIR = Path(__file__).absolute().parent / "support/mssql"


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
        image="mcr.microsoft.com/mssql/server:2017-CU25-ubuntu-16.04",
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

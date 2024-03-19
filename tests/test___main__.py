"""
SQL Runner has three command-line arguments that determine its behaviour: `dsn`,
`dummy-data-file`, and `output`. Each can take a string or None. If we set `output` to a
string (a path), then SQL Runner's behaviour is as follows:

| dsn  | dummy-data-file | Behaviour                         | Test                                                  |
|------|-----------------|-----------------------------------|-------------------------------------------------------|
| dsn  | path            | Query DB, write results to output | `test_entrypoint_with_dsn`                            |
| dsn  | None            | Query DB, write results to output | `test_entrypoint_with_dsn`                            |
| None | path            | Write dummy data file to output   | `test_entrypoint_without_dsn_with_dummy_data_file`    |
| None | None            | Write column headers to output    | `test_entrypoint_without_dsn_without_dummy_data_file` |
"""

import pathlib

import pytest

from sqlrunner import T1OOS_TABLE
from sqlrunner.__main__ import entrypoint


@pytest.fixture
def input_file(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    path = pathlib.Path("input.sql")
    path.write_text(
        f"-- {T1OOS_TABLE} intentionally not excluded\nSELECT 1 AS Patient_ID",
        "utf-8",
    )
    return str(path)


@pytest.mark.parametrize("pass_dummy_data_file", [False, True])
def test_entrypoint_with_dsn(
    monkeypatch, tmp_path, dsn, pass_dummy_data_file, input_file
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("os.environ", {"DATABASE_URL": dsn})

    argv = ["__main__", "--output", "output.csv", "--log-file", "log.json"]

    if pass_dummy_data_file:
        pathlib.Path("dummy_data.csv").touch()  # Notice the dummy data file is empty
        argv.extend(["--dummy-data-file", "dummy_data.csv"])

    argv.append(input_file)

    monkeypatch.setattr("sys.argv", argv)

    entrypoint()

    # The dummy data file is empty, so we can be confident that the output file contains
    # the result of executing the query in the input file against the database.
    assert pathlib.Path("output.csv").read_text("utf-8") == "Patient_ID\n1\n"

    # We test what is being logged elsewhere.
    assert pathlib.Path("log.json").exists()


def test_entrypoint_without_dsn_with_dummy_data_file(monkeypatch, tmp_path, input_file):
    monkeypatch.chdir(tmp_path)

    # The dummy data file and the query in the input file differ. Although this would be
    # a bug in a study, it allows us to test that the output file doesn't contain the
    # result of executing the query in the input file against the database.
    pathlib.Path("dummy_data.csv").write_text("Sex\nF\n", "utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "__main__",
            "--output",
            "output.csv",
            "--dummy-data-file",
            "dummy_data.csv",
            input_file,
        ],
    )

    entrypoint()

    assert pathlib.Path("output.csv").read_text("utf-8") == "Sex\nF\n"


def test_entrypoint_without_dsn_without_dummy_data_file(
    monkeypatch, tmp_path, input_file
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["__main__", "--output", "output.csv", input_file])
    entrypoint()
    assert pathlib.Path("output.csv").read_text("utf-8") == 'Patient_ID\n""\n'


def test_entrypoint_without_output(monkeypatch, tmp_path, input_file, capsys):
    # Without dsn, dummy-data-file, and (as the name of the test states) output. We
    # expect column headers to be written to stdout
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["__main__", input_file])
    entrypoint()
    out, _ = capsys.readouterr()
    assert out == 'Patient_ID\r\n""\r\n'

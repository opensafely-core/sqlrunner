import pathlib

from sqlrunner import T1OOS_TABLE
from sqlrunner.__main__ import entrypoint


def test_entrypoint(monkeypatch, tmp_path, dsn):
    monkeypatch.chdir(tmp_path)
    pathlib.Path("input.sql").write_text(
        f"-- {T1OOS_TABLE} intentionally not excluded\nSELECT 1 AS patient_id",
        "utf-8",
    )
    monkeypatch.setattr(
        "sys.argv",
        [
            "__main__",
            "--output",
            "output.csv",
            "--log-file",
            "log.json",
            "input.sql",
        ],
    )
    monkeypatch.setattr("os.environ", {"DATABASE_URL": dsn})
    entrypoint()
    assert pathlib.Path("output.csv").read_text("utf-8") == "patient_id\n1\n"
    assert pathlib.Path("log.json").exists()

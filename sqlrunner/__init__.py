from pathlib import Path


__version__ = Path(__file__).parent.joinpath("VERSION").read_text().strip()

T100S_TABLE = "PatientsWithTypeOneDissent"

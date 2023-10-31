from pathlib import Path


__version__ = Path(__file__).parent.joinpath("VERSION").read_text().strip()

T1OOS_TABLE = "PatientsWithTypeOneDissent"

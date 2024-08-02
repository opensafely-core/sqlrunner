from pathlib import Path


__version__ = Path(__file__).parent.joinpath("VERSION").read_text().strip()


# This table has its name for historical reasons, and reads slightly oddly: it should be
# interpreted as "allowed patients with regard to type one dissents"
T1OOS_TABLE = "AllowedPatientsWithTypeOneDissent"

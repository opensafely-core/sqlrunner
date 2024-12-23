from pathlib import Path


__version__ = Path(__file__).parent.joinpath("VERSION").read_text().strip()

# This is the name of the table listing patients with T1OOs.
T1OOS_TABLE = "PatientsWithTypeOneDissent"

# Previously we were given a table listing patients without T1OOs.
# The name should be interpreted as "allowed patients with regard to type one dissents".
OLD_T1OOS_TABLE = "AllowedPatientsWithTypeOneDissent"

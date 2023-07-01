from pathlib import Path

from rich.console import Console
import pandas as pd


def validate_file(console: Console, file: Path) -> None:
    """Validate an Excel sheet with persons against the Namescan emerald API."""
    console.log(f"Readings {file}")
    csv = pd.read_csv(file, nrows=10)
    for line in csv.iterrows():
        console.log(line)

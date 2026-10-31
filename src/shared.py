import re
from pathlib import Path

STOP = None

NON_LETTER_EDGES = re.compile(r"^[^A-Za-z]+|[^A-Za-z]+$")

PROJECT_DIR = Path(__file__).resolve().parents[1]

MODEL_DIR = PROJECT_DIR / "model"
CONFIG_PATH = PROJECT_DIR / "config.txt"
RESULTS_DIR = PROJECT_DIR / "data" / "results"



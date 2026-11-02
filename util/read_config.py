from pathlib import Path
from src.shared import PROJECT_DIR

# Read config.txt
def read_config(config_path):
    settings = {}
    for line in config_path.read_text().splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")

        if not separator:
            raise ValueError(f"Line is not key=value: {line!r}")
        settings[key.strip()] = value.strip()

    for key in ("image_dir", "n_workers"):
        if key not in settings:
            raise ValueError(f"{config_path.name} is missing {key}")

    # A relative image_dir is read from the project folder
    image_dir = Path(settings["image_dir"]).expanduser()
    if not image_dir.is_absolute():
        image_dir = PROJECT_DIR / image_dir
    if not image_dir.is_dir():
        raise ValueError(f"image_dir is not a folder: {image_dir}")

    n_workers = int(settings["n_workers"])
    if n_workers < 1:
        raise ValueError("n_workers must be at least 1")

    return image_dir, n_workers
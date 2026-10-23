# Run OCR on one image

import argparse
from pathlib import Path
import shutil

from PIL import Image, ImageOps
import pytesseract


MODEL_DIR = Path(__file__).resolve().parent / "model"


def recognize_text(image_path: Path) -> str:
    with Image.open(image_path) as image:
        grayscale = ImageOps.grayscale(image)

    # Treat the image as one word
    return pytesseract.image_to_string(
        grayscale,
        lang="eng",
        config=f'--tessdata-dir "{MODEL_DIR}" --psm 8',
        timeout=30,
    ).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="Path to one image file")
    args = parser.parse_args()

    if not args.image.is_file():
        parser.error(f"Image file not found: {args.image}")
    if not (MODEL_DIR / "eng.traineddata").is_file():
        parser.error(f"English model not found in: {MODEL_DIR}")
    if shutil.which("tesseract") is None:
        parser.exit(1, "Tesseract is missing from PATH. See README.md for setup.\n")

    try:
        text = recognize_text(args.image)
    except (OSError, RuntimeError) as error:
        parser.exit(1, f"OCR failed: {error}\n")

    if not text:
        parser.exit(1, "No text was recognized in this image.\n")
    print(text)


if __name__ == "__main__":
    main()

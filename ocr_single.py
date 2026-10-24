import argparse
import re
import shutil
import pytesseract

from pathlib import Path
from PIL import Image, ImageFilter, ImageOps



MODEL_DIR = Path(__file__).resolve().parent / "model"
NON_LETTER_EDGES = re.compile(r"^[^A-Za-z]+|[^A-Za-z]+$")


def recognize_text(image_path):
    with Image.open(image_path) as image:
        return recognize_image(image)


def recognize_image(image):
    # Preprocess an already opened image and run OCR on it
    grayscale = ImageOps.grayscale(image)

    # Remove salt and pepper noise (using 3x3 median filter)
    denoised = grayscale.filter(ImageFilter.MedianFilter(3))

    text = pytesseract.image_to_string(
        denoised,
        lang="eng",
        # --psm 3 analyzes the layout and crops a tight text line around the word
        # --psm 8 skips that step, so the text region stretches to include specks
        config=f'--tessdata-dir "{MODEL_DIR}" --psm 3',
        timeout=30,
    )

    # Remove non-letter characters at the start and end only
    return NON_LETTER_EDGES.sub("", text)


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

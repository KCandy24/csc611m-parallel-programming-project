# CSC611M parallel OCR pipeline

For now, this runs OCR on one image. It converts the image to grayscale, uses
the English model in `model/eng.traineddata`, and prints the text in the terminal.

## Setup

You need Python 3.10 or newer and Tesseract. Run the commands below from the
project folder.

### Mac

Install Tesseract with Homebrew:

```sh
brew install tesseract
```

Create a virtual environment and install the Python packages:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Windows

Install Tesseract using the Windows section of the
[installation guide](https://tesseract-ocr.github.io/tessdoc/Installation.html).
Add the folder containing `tesseract.exe` to your PATH, then open a new
Command Prompt.

In Command Prompt, create a virtual environment and install the Python packages:

```bat
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
```

### Check the installation

On either system, check that Tesseract is available:

```text
tesseract --version
```

`requirements.txt` installs Pillow for opening images and pytesseract for calling
Tesseract from Python. Tesseract itself needs the separate installation above.

## Run one image

With the virtual environment activated, run this on either system:

```sh
python ocr_single.py data/dataset/img0002.png
```

The word in this image is `grape`. During the Mac test, the output was `- grape`,
so it picked up the word but added a hyphen. The images have noise, so the output
can have extra characters or wrong letters.

Change the image path to try another image. If the path has spaces, put it in
quotes. `labels.txt` lists the expected words for checking the output. The script
does not read the labels to get its answer.

The script uses `--psm 8`, which tells Tesseract to treat the image as one word.

Tested on Mac with Python 3.14.4, Tesseract 5.5.3, Pillow 12.3.0, and pytesseract
0.3.13. The Windows setup still needs testing.

## Next steps

Add the loader, shared queue, multiple OCR workers, and CSV output. After that,
test different worker counts and prepare the slides.

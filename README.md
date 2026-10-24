# CSC611M parallel OCR pipeline

For now, this runs OCR on one image. It converts the image to grayscale, removes
noise with a 3x3 median filter, uses the English model in `model/eng.traineddata`,
and prints the text in the terminal.

## Setup

You need Python 3.10 or newer, Anaconda/Miniconda, and Tesseract. Run the commands below from the project folder.

```sh
conda env create -f env.yaml
conda activate tesseract-env
```

### Check the installation

On either system, once (tesseract-env) is seen at the start of the command line prompt, 
check that Tesseract is available:

```text
tesseract --version
```

## Run one image

With the conda environment activated, run this on either system:

```sh
python ocr_single.py data/dataset/img0002.png
```

The word in this image is `grape`, and the script prints `grape`. After OCR, it
removes non-letter characters at the start and end of the text, such as a stray
`:` or `-`. The images have noise, so some outputs can still have wrong letters.

Change the image path to try another image. If the path has spaces, put it in
quotes. `labels.txt` lists the expected words for checking the output. The script
does not read the labels to get its answer.

The script uses `--psm 3`, Tesseract's default automatic page layout. On the
100-image dataset, the median filter with `--psm 3` gave more exact matches than
`--psm 8`, which treats the image as one word.

## Next steps

Add the loader, shared queue, multiple OCR workers, and CSV output. After that,
test different worker counts and prepare the slides.

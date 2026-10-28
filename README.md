# CSC611M parallel OCR pipeline

One loader process puts the images from `image_dir` on a shared queue. `n_workers`
OCR worker processes take images from the queue. Each worker converts the image
to grayscale, removes noise with a 3x3 median filter, and runs OCR with the
English model in `model/eng.traineddata`. One writer process saves the results
to a CSV in `data/results/`.

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

## Run the pipeline

Set the image folder and the number of OCR workers in `config.txt`:

```text
image_dir=data/dataset
n_workers=2
```

With the conda environment activated, run this on either system:

```sh
python main.py
```

After OCR, each worker removes non-letter characters at the start and end of the
text, such as a stray `:` or `-`. The images have noise, so some outputs can still
have wrong letters. `labels.txt` lists the expected words for checking the output.
The pipeline does not read the labels to get its answer.

The workers use `--psm 3`, Tesseract's default automatic page layout. On the
100-image dataset, the median filter with `--psm 3` gave more exact matches than
`--psm 8`, which treats the image as one word.

## Next steps

Make the pipeline exit cleanly, fix the CSV output, test different worker counts,
and prepare the slides.

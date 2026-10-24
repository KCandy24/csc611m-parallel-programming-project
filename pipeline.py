import queue
import threading

from pathlib import Path
from PIL import Image
from ocr_single import recognize_image


PROJECT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = PROJECT_DIR / "config.txt"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}

# Put on the queue by the loader to tell a worker there are no more images
STOP = None

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



# Load images, share a queue, and run one OCR worker
def loader(image_dir, image_queue):
    # Load every image in image_dir and put it on the queue
    image_paths = sorted(
        path for path in image_dir.iterdir()
        if path.suffix.lower() in IMAGE_EXTENSIONS
    )
    try:
        for image_id, path in enumerate(image_paths, start=1):
            with Image.open(path) as image:
                # read the pixels now, so the file can close
                image.load()  
            image_queue.put((image_id, path.name, image))
    finally:
        # Always send STOP, even if loading fails, so the worker never waits forever
        image_queue.put(STOP)


def ocr_worker(image_queue):
    # Take images from the queue and run OCR until STOP arrives.
    while True:
        item = image_queue.get()
        if item is STOP:
            break
        image_id, filename, image = item
        text = recognize_image(image)
        print(f"{image_id}\t{filename}\t{text}")


def main():
    image_dir, n_workers = read_config(CONFIG_PATH)
    print(f"image_dir={image_dir}")
    print(f"n_workers={n_workers} (stage 2 still uses 1 worker)")

    image_queue = queue.Queue()

    loader_thread = threading.Thread(
        target=loader, args=(image_dir, image_queue), name="loader"
    )
    worker_thread = threading.Thread(
        target=ocr_worker, args=(image_queue,), name="ocr-worker-1"
    )

    loader_thread.start()
    worker_thread.start()

    # Wait for both threads to finish before the program ends
    loader_thread.join()
    worker_thread.join()
    print("All images processed.")


if __name__ == "__main__":
    main()

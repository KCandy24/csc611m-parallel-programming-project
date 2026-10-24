import queue
import threading

from pathlib import Path
from PIL import Image
from ocr_single import recognize_image


PROJECT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = PROJECT_DIR / "config.txt"

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



# Load images, share a queue, and run n OCR workers
def loader(image_dir, image_queue, n_workers):
    # Load every PNG image in image_dir and put it on the queue
    image_paths = sorted(image_dir.glob("*.png"))
    try:
        for image_id, path in enumerate(image_paths, start=1):
            with Image.open(path) as image:
                # read the pixels now, so the file can close
                image.load()  
            image_queue.put((image_id, path.name, image))
    finally:
        # Send one STOP per worker, even if loading fails, so no worker waits forever
        # Every image is taken before any STOP
        for _ in range(n_workers):
            image_queue.put(STOP)


def ocr_worker(image_queue):
    # Take images from the queue and run OCR until STOP arrives
    worker_name = threading.current_thread().name
    while True:
        item = image_queue.get()
        if item is STOP:
            break
        image_id, filename, image = item
        text = recognize_image(image)
        print(f"{image_id}\t{filename}\t{text}\t{worker_name}")


def main():
    image_dir, n_workers = read_config(CONFIG_PATH)
    print(f"image_dir={image_dir}")
    print(f"n_workers={n_workers}")

    image_queue = queue.Queue()

    loader_thread = threading.Thread(
        target=loader, args=(image_dir, image_queue, n_workers), name="loader"
    )
    worker_threads = [
        threading.Thread(
            target=ocr_worker, args=(image_queue,), name=f"ocr-worker-{number}"
        )
        for number in range(1, n_workers + 1)
    ]

    loader_thread.start()
    for worker_thread in worker_threads:
        worker_thread.start()

    # Wait for every thread to finish before the program ends
    loader_thread.join()
    for worker_thread in worker_threads:
        worker_thread.join()
    print("All images processed.")


if __name__ == "__main__":
    main()

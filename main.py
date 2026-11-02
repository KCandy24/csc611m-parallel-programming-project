from src.ocr_manager import OCR_Manager
from src.shared import CONFIG_PATH, RESULTS_DIR
from util.read_config import read_config


def main():
    image_dir, n_workers = read_config(CONFIG_PATH)
    print(f"image_dir={image_dir}")
    print(f"n_workers={n_workers}")

    # The spec asks for a single "ocr_results.csv"
    manager = OCR_Manager(image_dir= image_dir, n_workers= n_workers, file_name= "ocr_results")
    file_name, elapsed_ms = manager.dispatch_workers()

    print(f"Total time: {elapsed_ms:.4f} ms")
    print(f"Results saved to: {RESULTS_DIR / (file_name + '.csv')}")

if __name__ == "__main__":
    main()

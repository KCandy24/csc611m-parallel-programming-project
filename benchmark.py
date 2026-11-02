import os

from src.ocr_manager import OCR_Manager
from src.shared import CONFIG_PATH, RESULTS_DIR
from util.read_config import read_config
from util.report import generate_report

BENCHMARK_DIR = RESULTS_DIR / "benchmark"


def worker_counts():
    return list(range(1, (os.cpu_count() or 1) + 1))


def main():
    image_dir, _ = read_config(CONFIG_PATH)
    counts = worker_counts()
    print(f"image_dir={image_dir}")
    print(f"worker counts={counts}")

    runs = []
    for n_workers in counts:
        manager = OCR_Manager(
            image_dir= image_dir,
            n_workers= n_workers,
            file_name= f"ocr_results_{n_workers}_workers",
            results_dir= BENCHMARK_DIR
        )
        file_name, elapsed_ms = manager.dispatch_workers()
        print(f"{n_workers} workers: {elapsed_ms:.4f} ms")

        runs.append({
            "workers": n_workers,
            "time_ms": elapsed_ms,
            "csv": BENCHMARK_DIR / (file_name + ".csv"),
        })

    generate_report(runs= runs, data_dir= image_dir)

if __name__ == "__main__":
    main()

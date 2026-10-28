from multiprocessing import Process
from pathlib import Path
import csv
from src.shared import STOP, RESULTS_DIR

class CSV_Writer(Process):

    def __init__(self, result_queue, file_name):
        super().__init__()
        self.result_queue = result_queue
        self.csv_path = RESULTS_DIR / (file_name + ".csv")
        
    def run(self):
        print(f"Writer started.")

        # Create data/results if it does not exist yet
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

        # "w" replaces the file from the last run instead of adding to it
        with open(self.csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "filename", "text", "worker", "time_ms"])

            while True:
                line = self.result_queue.get()
                if line is STOP:
                    break

                writer.writerow(line)
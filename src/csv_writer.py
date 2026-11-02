from multiprocessing import Process
import csv
from src.shared import STOP, RESULTS_DIR

class CSV_Writer(Process):

    def __init__(self, result_queue, file_name, results_dir=RESULTS_DIR):
        super().__init__()
        self.result_queue = result_queue
        self.results_dir = results_dir
        self.csv_path = results_dir / (file_name + ".csv")
        
    def run(self):
        print(f"Writer started.")

        # Create the results folder if it does not exist yet
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # "w" replaces the file from the last run instead of adding to it
        with open(self.csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "filename", "text", "worker", "time_ms"])

            while True:
                line = self.result_queue.get()
                if line is STOP:
                    break

                writer.writerow(line)
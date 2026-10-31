from multiprocessing import Queue
import time

from src.ocr_worker import OCR_Worker
from src.loader import Loader
from src.csv_writer import CSV_Writer
from src.shared import STOP

class OCR_Manager():

    def __init__(self, image_dir, n_workers):
        self.n_workers = n_workers

        self.image_queue = Queue()
        self.result_queue = Queue()
        self.file_name = f"ocr_results_{n_workers}_threads"

        
        self.loader = Loader(
            image_paths= sorted(image_dir.glob("*.png")), 
            n_workers= self.n_workers,
            image_queue= self.image_queue
        )
        
        self.writer = CSV_Writer(
            result_queue= self.result_queue,
            file_name= self.file_name
        )


    def dispatch_workers(self):

        start_time = time.perf_counter_ns()

        worker_processes = []

        self.loader.start()

        self.writer.start()


        for number in range(1, self.n_workers + 1):
            worker = OCR_Worker( 
                worker_id= number,
                image_queue= self.image_queue,
                result_queue= self.result_queue
            )
            worker_processes.append(worker)
            worker.start()


        for worker in worker_processes:
            worker.join()
            if worker.exitcode != 0:
                print(f"{worker.name} stopped with exit code {worker.exitcode}")

        # All workers are done, so no more results will come. Tell the writer to stop.
        self.result_queue.put(STOP)

        self.writer.join()

        self.loader.join()

        elapsed_ns = time.perf_counter_ns() - start_time
        return self.file_name, elapsed_ns / 1_000_000



        


            
        
        

    
    
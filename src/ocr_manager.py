from multiprocessing import Queue

from src.ocr_worker import OCR_Worker
from src.loader import Loader
from src.csv_writer import CSV_Writer
from src.shared import STOP

class OCR_Manager():

    def __init__(self, image_dir, n_workers):
        self.n_workers = n_workers

        self.image_queue = Queue()
        self.result_queue = Queue()

        
        self.loader = Loader(
            image_paths= sorted(image_dir.glob("*.png")), 
            n_workers= self.n_workers,
            image_queue= self.image_queue
        )
        
        self.writer = CSV_Writer(
            result_queue= self.result_queue,
            file_name= "ocr_results"
        )


    def dispatch_workers(self):

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


        


            
        
        

    
    
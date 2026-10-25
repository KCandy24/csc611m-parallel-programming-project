#  
# OCR Worker class: This handles one process of OCR
# 

from src.shared import MODEL_DIR, NON_LETTER_EDGES, STOP

import pytesseract
import time

import multiprocessing
from multiprocessing import Process
from PIL import ImageFilter, ImageOps

class OCR_Worker(Process):

    def __init__(self, worker_id, image_queue, result_queue):
        super().__init__()
        self.worker_id = worker_id
        self.image_queue = image_queue
        self.result_queue = result_queue

    def recognize_image(self, image):
        # Preprocess an already opened image and run OCR on it
        grayscale = ImageOps.grayscale(image)

        # Remove salt and pepper noise (using 3x3 median filter)
        denoised = grayscale.filter(ImageFilter.MedianFilter(3))

        start_time = time.perf_counter_ns()

        text = pytesseract.image_to_string(
            denoised,
            lang="eng",
            # --psm 3 analyzes the layout and crops a tight text line around the word
            # --psm 8 skips that step, so the text region stretches to include specks
            config=f'--tessdata-dir "{MODEL_DIR}" --psm 3',
            timeout=30,
        )
        elapsed_ns = time.perf_counter_ns() - start_time

        # Remove non-letter characters at the start and end only
        ## Also return the time in miliseconds
        return NON_LETTER_EDGES.sub("", text), elapsed_ns / 100
    
    def run(self):
        print(f"Worker {self.worker_id} started.")
        worker_name = multiprocessing.current_process().name

        while True:
            item = self.image_queue.get()

            if item is STOP:
                break

            image_id, filename, image = item

            text, time = self.recognize_image(image)

            print(f"{image_id},{filename},{text},{worker_name},{time:.4f}ms")
            self.result_queue.put([image_id, filename, text, worker_name, f"{time:.4f}ms"])
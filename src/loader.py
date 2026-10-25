from multiprocessing import Process
from PIL import Image

from src.shared import STOP

class Loader(Process):
    def __init__(self, image_paths, n_workers, image_queue): # We add the global shared vars/semaphore here
        super().__init__()
        self.image_paths = image_paths
        self.n_workers = n_workers
        self.image_queue = image_queue

    def run(self):
        print(f"Loader started.")

        for image_id, path in enumerate(self.image_paths, start=1):
            
            with Image.open(path) as image:
                # read the pixels now, so the file can close
                image.load()  
            self.image_queue.put((image_id, path.name, image))

        for _ in range(self.n_workers):
            self.image_queue.put(STOP)

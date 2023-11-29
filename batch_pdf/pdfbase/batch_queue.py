from typing import Callable
from queue import Queue, Full

class BatchedQueue:
    def __init__(self, consume_func: Callable, batch_size = None ) -> None:
        self.batch_size = batch_size
        self.consume_func = consume_func
        self.items = Queue(batch_size)

    def add(self, item):
        try:
            self.items.put_nowait(item)
        except Full:
            self.consume_func(self.items)
    
    def last_job(self):
        if self.items.empty():
            return False
        self.consume_func(self.items)
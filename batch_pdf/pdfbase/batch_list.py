from typing import Callable

class BatchedList:
    def __init__(self, consume_func: Callable, batch_size = None ) -> None:
        self.batch_size = batch_size
        self.consume_func = consume_func
        self.items = []

    def add(self, item):
        if len(self.items) < self.batch_size:
            self.items.append(item)
        else:
            self.consume_func(self.items)
            self.items.append(item)
    
    def last_job(self):
        if len(self.items) == 0:
            return False
        self.consume_func(self.items)
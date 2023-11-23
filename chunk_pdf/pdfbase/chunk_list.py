class ListFull(Exception):
    pass

class ChukedList:
    def __init__(self, chunkSize = 10) -> None:
        self.chunkSize = chunkSize
        self.items = []

    def append(self, item):
        if len(self.items) < self.chunkSize:
            self.items.append(item)
        else:
            raise ListFull()
            
    def convertBytes(self):
        convert_bytes = b''.join(self.items)
        self.items.clear()
        return convert_bytes
    
    def is_empty(self):
        return len(self.items) == 0
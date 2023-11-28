from io import FileIO

KB = 1024
MB = 1024 * 1024

class ChunkedFileIO:
    def __init__(self, chunk_size = None) -> None:
        self.chunk_size = chunk_size

    def file_write(self, data: bytes, file_io: FileIO):
        total_bytes = len(data)
        bytes_written = 0

        while bytes_written < total_bytes:
            chunked_data = data[bytes_written:bytes_written + self.chunk_size]
            file_io.write(chunked_data)

            bytes_written += len(chunked_data)
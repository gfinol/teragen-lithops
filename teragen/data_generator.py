from teragen.data_iterator import DataIterator


class DataGenerator(object):
    """
    A file-like object which generates data for the TeraSort benchmark.

    Never actually keeps all the data in memory so can be used to generate huge data sets.
    """

    def __init__(self, data_iterator: 'DataIterator'):
        self.data_iterator = data_iterator
        self.BLOCK_SIZE_BYTES = 100

        self.bytes_total = len(data_iterator) * self.BLOCK_SIZE_BYTES
        self.pos = 0

        self.current_block_data = b""
        self.current_block_pos = 0

    @staticmethod
    def create_data_generator(index: int, records_per_partition: int, is_ascii: bool = False):
        return DataGenerator(DataIterator(index, records_per_partition, is_ascii))

    def __len__(self) -> int:
        return self.bytes_total

    @property
    def len(self) -> int:
        return self.bytes_total

    def tell(self) -> int:
        return self.pos

    def get_next_block(self) -> bytes:
        return next(self.data_iterator)

    def read(self, bytes_requested: int) -> bytes:

        remaining_bytes = self.bytes_total - self.pos
        if remaining_bytes == 0:
            return b''

        if bytes_requested < 0:
            bytes_out = remaining_bytes
        else:
            bytes_out = min(remaining_bytes, bytes_requested)

        byte_data = b''
        byte_pos = 0
        while byte_pos < bytes_out:

            bytes_remaining = bytes_out - byte_pos

            needed_data_from_current_block = min(bytes_remaining, self.BLOCK_SIZE_BYTES - self.current_block_pos)

            chunk = self.current_block_data[self.current_block_pos:self.current_block_pos + needed_data_from_current_block]
            byte_data += chunk
            byte_pos += len(chunk)
            self.current_block_pos = (self.current_block_pos + needed_data_from_current_block) % self.BLOCK_SIZE_BYTES

            if self.current_block_pos == 0 and remaining_bytes - byte_pos > 0:
                self.current_block_data = self.get_next_block()

        self.pos += bytes_out

        return byte_data

    def seek(self, byte_num: int):
        if byte_num < 0:
            raise ValueError("Seek position must be non-negative")
        if byte_num >= self.bytes_total:
            raise ValueError("Seek position must be less than total number of bytes")

        self.pos = byte_num
        self.data_iterator.seek(byte_num // self.BLOCK_SIZE_BYTES)
        self.current_block_data = self.get_next_block()
        self.current_block_pos = byte_num % self.BLOCK_SIZE_BYTES
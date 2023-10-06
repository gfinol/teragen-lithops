import numpy as np

from teragen.records_generators import RECORD_LEN, generate_ascii_record, generate_record
from teragen.random16 import Random16
from teragen.unsigned16 import Unsigned16


class DataIterator:

    def __init__(self, index: int, records_per_partition: int, is_ascii: bool = False):
        self.index = index
        self.records_per_partition = records_per_partition
        self.is_ascii = is_ascii

        self.one = Unsigned16(1)
        self.first_record_number = Unsigned16(self.index * self.records_per_partition)
        self.records_to_generate = Unsigned16(self.records_per_partition)

        self.record_number = Unsigned16(self.first_record_number)
        self.last_record_number = Unsigned16(self.first_record_number)
        self.last_record_number.add(self.records_to_generate)

        self.rand = Random16.skip_ahead(self.first_record_number)

        self.rowBytes = bytearray(RECORD_LEN)

    def __iter__(self):
        self.rand = Random16.skip_ahead(self.first_record_number)
        self.record_number = Unsigned16(self.first_record_number)
        return self

    def __next__(self):
        if self.record_number.value >= self.last_record_number.value:
            raise StopIteration
        else:
            Random16.next_rand(self.rand)
            if self.is_ascii:
                generate_ascii_record(self.rowBytes, self.rand, self.record_number)
            else:
                generate_record(self.rowBytes, self.rand, self.record_number)
            self.record_number.add(self.one)
            return bytes(self.rowBytes)

    def __len__(self):
        return self.records_per_partition

    def seek(self, record_number: int):
        self.record_number = Unsigned16(record_number)
        self.record_number.add(self.first_record_number)
        self.rand = Random16.skip_ahead(self.record_number)


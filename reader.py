# -*- coding: utf-8 -*-

import struct


class ReaderException(Exception):
    pass

class Reader:
    def __init__(self, buf):
        self.buf = buf

    def tell(self):
        return self.buf.tell()

    def seek(self, offset):
        self.buf.seek(offset)

    def read_int(self):
        return struct.unpack('>I', self.buf.read(4))[0]

    def skip(self, offset):
        self.buf.read(offset)

    def read(self, offset):
        return self.buf.read(offset)

    def read_str(self):
        length = self.read_int()
        return self.read(length).decode('utf-8')

    def error(self, msg):
        print(msg.format(offset=self.tell()))
        raise ReaderException()

    def end(self):
        offset = self.tell()
        if offset != self.buf.seek(0, 2):
            self.error('Not ended buffer')


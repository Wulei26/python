import os
import sys

"""
判断文件的压缩类型
"""
BLOCKSIZE = 512

FILEREADMODE = os.O_RDONLY


class _FileStream:
    """Low-level file object. Supports reading and writing.
    It is used instead of a regular file object for streaming
    access.
    """

    def __init__(self, filepath: str, mode: str):
        mode = {
            "r": os.O_RDONLY,
            "w": os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
        }[mode]
        if hasattr(os, "O_BINARY"):
            mode |= os.O_BINARY
        self.filestream = os.open(filepath, mode, 0o666)

    def close(self):
        os.close(self.filestream)

    def read(self, size):
        return os.read(self.filestream, size)

    def write(self, s):
        os.write(self.filestream, s)


class _StreamProxy(object):
    """Small proxy class that enables transparent compression
    detection for the Stream interface (mode 'r|*').
    """

    def __init__(self, filepath: str, mode: str):
        self.fileobj = _FileStream(filepath, mode)
        self.buf = self.fileobj.read(BLOCKSIZE)

    @classmethod
    def get_filebuf(cls, filepath: str, mode: str):
        return _StreamProxy(filepath, mode).buf

    def close(self):
        self.fileobj.close()


class FileType:
    _instance = None

    """
    获取一个512字节的文件流
    """

    def __init__(self, filepath: str, mode: str):
        self.buf = _StreamProxy.get_filebuf(filepath, mode)

    """
    通过文件魔数识别文件的压缩类型
    """

    @classmethod
    def get_compression_type(cls, filepath: str, mode: str) -> str:
        if cls._instance is None:
            cls._instance = cls(filepath, mode)
        buf = cls._instance.buf
        if buf.startswith(b"\x1f\x8b\x08"):
            return "gz"
        elif buf[0:3] == b"BZh" and buf[4:10] == b"1AY&SY":
            return "bz2"
        elif buf.startswith((b"\x5d\x00\x00\x80", b"\xfd7zXZ")):
            return "xz"
        elif (
            buf.startswith(b"\x50\x4b\x03\x04")
            or buf.startswith(b"\x50\x4b\x05\x06")
            or buf.startswith(b"\x50\x4b\x07\x08")
        ):
            return "zip"
        elif buf.startswith(b"Rar!\x1a\x07\x00") or buf.startswith(
            b"Rar!\x1a\x07\x01\x00"
        ):
            return "rar"
        else:
            return "Unrecognize"


if __name__ == "__main__":
    a = FileType("D:/python_tutorial/ERR3218373.fastq.gz", "r")
    print(FileType.get_compression_type("D:/python_tutorial/ERR3218373.fastq.gz", "r"))

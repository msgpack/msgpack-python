class MsgpackBaseException(Exception):
    pass


class UnpackException(MsgpackBaseException):
    pass


class BufferFull(UnpackException):
    pass


class OutOfData(UnpackException):
    pass


class UnpackValueError(UnpackException, ValueError):
    pass


class ExtraData(ValueError):
    def __init__(self, unpacked, extra):
        self.unpacked = unpacked
        self.extra = extra

    def __str__(self):
        return "unpack(b) received extra data."

class PackException(MsgpackBaseException):
    pass

class PackValueError(PackException, ValueError):
    pass


class PackOverflowError(PackValueError, OverflowError):
    pass

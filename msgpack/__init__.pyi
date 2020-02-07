import sys
from typing import (
    Any,
    BinaryIO,
    Callable,
    Collection,
    Dict,
    Generic,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

if sys.version_info >= (3, 8):
    from typing import Protocol
    class SupportsRead(Protocol):
        def read(self, amount: Optional[int] = ...) -> bytes: ...
    class SupportsWrite(Protocol):
        def write(self, data: Union[bytes, bytearray]) -> Optional[int]: ...

else:
    SupportsRead = BinaryIO
    SupportsWrite = BinaryIO

_S = TypeVar("_S", bound=SupportsRead)

_ObjectHook = Callable[[Dict[Any, Any]], Any]
_ObjectPairsHook = Callable[[Iterator[Tuple[Any, Any]]], Any]
_ListHook = Callable[[List[Any]], Any]
_UserTypeConverter = Callable[[Any], Any]

class UnpackException(Exception): ...
class BufferFull(UnpackException): ...
class OutOfData(UnpackException): ...
class FormatError(ValueError, UnpackException): ...
class StackError(ValueError, UnpackException): ...

UnpackValueError = ValueError

class ExtraData(UnpackValueError):
    unpacked: Any = ...
    extra: bytearray = ...
    def __init__(self, unpacked: Any, extra: bytearray) -> None: ...

PackException = Exception
PackValueError = ValueError
PackOverflowError = OverflowError

class ExtType(NamedTuple):
    code: Union[int, bytes]
    data: bytes

class Unpacker(Generic[_S]):
    _U = TypeVar("_U", bound="Unpacker[_S]")
    file_like: Optional[_S]
    def __init__(
        self,
        file_like: Optional[_S] = ...,
        read_size: int = ...,
        use_list: bool = ...,
        raw: bool = ...,
        strict_map_key: bool = ...,
        object_hook: Optional[_ObjectHook] = ...,
        object_pairs_hook: Optional[_ObjectPairsHook] = ...,
        list_hook: Optional[_ListHook] = ...,
        encoding: Optional[str] = ...,
        unicode_errors: Optional[str] = ...,
        max_buffer_size: int = ...,
        ext_hook: Type[ExtType] = ...,
        max_str_len: int = ...,
        max_bin_len: int = ...,
        max_array_len: int = ...,
        max_map_len: int = ...,
        max_ext_len: int = ...,
    ) -> None: ...
    def feed(self, next_bytes: Union[bytes, bytearray, memoryview]) -> None: ...
    def read_bytes(self, n: int) -> bytearray: ...
    def __iter__(self: _U) -> _U: ...
    def __next__(self) -> Any: ...
    def skip(self) -> None: ...
    def unpack(self) -> Any: ...
    def read_array_header(self) -> int: ...
    def read_map_header(self) -> int: ...
    def tell(self) -> int: ...

class Packer:
    def __init__(
        self,
        default: Optional[_UserTypeConverter] = ...,
        encoding: Optional[str] = ...,
        unicode_errors: Optional[str] = ...,
        use_single_float: bool = ...,
        autoreset: bool = ...,
        use_bin_type: bool = ...,
        strict_types: bool = ...,
    ) -> None: ...
    def pack(self, obj: Any) -> bytes: ...
    def pack_map_pairs(self, pairs: Collection[Tuple[Any, Any]]) -> bytes: ...
    def pack_array_header(self, n: int) -> bytes: ...
    def pack_map_header(self, n: int) -> bytes: ...
    def pack_ext_type(self, typecode: int, data: bytes) -> None: ...
    def bytes(self) -> bytes: ...
    def reset(self) -> None: ...
    def getbuffer(self) -> memoryview: ...

def pack(
    o: Any,
    stream: SupportsWrite,
    default: Optional[_UserTypeConverter] = ...,
    encoding: Optional[str] = ...,
    unicode_errors: Optional[str] = ...,
    use_single_float: bool = ...,
    autoreset: bool = ...,
    use_bin_type: bool = ...,
    strict_types: bool = ...,
) -> None: ...
def packb(
    o: Any,
    encoding: Optional[str] = ...,
    unicode_errors: Optional[str] = ...,
    use_single_float: bool = ...,
    autoreset: bool = ...,
    use_bin_type: bool = ...,
    strict_types: bool = ...,
) -> bytes: ...
def unpack(
    stream: SupportsRead,
    read_size: int = ...,
    use_list: bool = ...,
    raw: bool = ...,
    strict_map_key: bool = ...,
    object_hook: Optional[_ObjectHook] = ...,
    object_pairs_hook: Optional[_ObjectPairsHook] = ...,
    list_hook: Optional[_ListHook] = ...,
    encoding: Optional[str] = ...,
    unicode_errors: Optional[str] = ...,
    max_buffer_size: int = ...,
    ext_hook: Type[ExtType] = ...,
    max_str_len: int = ...,
    max_bin_len: int = ...,
    max_array_len: int = ...,
    max_map_len: int = ...,
    max_ext_len: int = ...,
) -> Any: ...
def unpackb(
    packed: bytes,
    read_size: int = ...,
    use_list: bool = ...,
    raw: bool = ...,
    strict_map_key: bool = ...,
    object_hook: Optional[_ObjectHook] = ...,
    object_pairs_hook: Optional[_ObjectPairsHook] = ...,
    list_hook: Optional[_ListHook] = ...,
    encoding: Optional[str] = ...,
    unicode_errors: Optional[str] = ...,
    max_buffer_size: int = ...,
    ext_hook: Type[ExtType] = ...,
    max_str_len: int = ...,
    max_bin_len: int = ...,
    max_array_len: int = ...,
    max_map_len: int = ...,
    max_ext_len: int = ...,
) -> Any: ...

load = unpack
loads = unpackb
dump = pack
dumps = packb

version: Tuple[int, int, int]

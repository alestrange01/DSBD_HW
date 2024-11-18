from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class NoneRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RegisterRequest(_message.Message):
    __slots__ = ("email", "password", "share")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    SHARE_FIELD_NUMBER: _ClassVar[int]
    email: str
    password: str
    share: str
    def __init__(self, email: _Optional[str] = ..., password: _Optional[str] = ..., share: _Optional[str] = ...) -> None: ...

class LoginRequest(_message.Message):
    __slots__ = ("email", "password")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    email: str
    password: str
    def __init__(self, email: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class UpdateRequest(_message.Message):
    __slots__ = ("email", "share")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    SHARE_FIELD_NUMBER: _ClassVar[int]
    email: str
    share: str
    def __init__(self, email: _Optional[str] = ..., share: _Optional[str] = ...) -> None: ...

class DeleteRequest(_message.Message):
    __slots__ = ("email",)
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    email: str
    def __init__(self, email: _Optional[str] = ...) -> None: ...

class MeanRequest(_message.Message):
    __slots__ = ("n",)
    N_FIELD_NUMBER: _ClassVar[int]
    n: str
    def __init__(self, n: _Optional[str] = ...) -> None: ...

class Reply(_message.Message):
    __slots__ = ("statusCode", "message", "content")
    STATUSCODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    statusCode: str
    message: str
    content: str
    def __init__(self, statusCode: _Optional[str] = ..., message: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

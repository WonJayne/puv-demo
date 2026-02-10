from typing import IO, TypeVar


def skip_one_line_in_file(file_handle: IO) -> None:
    next(file_handle)


IterT = TypeVar("IterT")

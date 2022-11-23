import sys
from io import StringIO
from typing import TextIO, Union


class RedirectedStdout(object):
    '''
    https://stackoverflow.com/a/45899925
    '''

    _stdout: Union[TextIO, None]
    _string_io: Union[StringIO, None]

    def __init__(self) -> None:
        self._stdout = None
        self._string_io = None

    def __enter__(self) -> 'RedirectedStdout':
        self._stdout = sys.stdout
        sys.stdout = self._string_io = StringIO()
        return self

    def __exit__(self, type, value, traceback) -> None:
        sys.stdout = self._stdout

    def __str__(self) -> str:
        return self._string_io.getvalue()

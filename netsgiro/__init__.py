from typing import Any, List, Optional  # noqa

import attr

from netsgiro import records


__version__ = '0.1.0'


@attr.s
class Container:
    start_record = attr.ib()
    end_record = attr.ib()
    contents = attr.ib()

    _start_record_class = None  # type: Optional[records.Record]
    _end_record_class = None  # type: Optional[records.Record]
    _contents_class = None  # type: Any

    @classmethod
    def from_ocr(cls, lines: List[str]) -> 'Container':
        if len(lines) < 2:
            raise ValueError('Container must have at least two lines')

        for line in lines:
            if len(line) != 80:
                raise ValueError('All lines must be exactly 80 chars long')

        start_line, lines, end_line = lines[0], lines[1:-1], lines[-1]

        start_record = cls._start_record_class.from_string(start_line)
        end_record = cls._end_record_class.from_string(end_line)

        if lines and cls._contents_class is not None:
            contents = cls._contents_class.from_ocr(lines)
        else:
            contents = None

        return cls(
            start_record=start_record,
            end_record=end_record,
            contents=contents,
        )


@attr.s
class Assignment(Container):
    _start_record_class = records.AssignmentStart
    _end_record_class = records.AssignmentEnd
    _contents_class = None  # type: Any


@attr.s
class Transmission(Container):
    _start_record_class = records.TransmissionStart
    _end_record_class = records.TransmissionEnd
    _contents_class = Assignment


def parse(data: str) -> Container:
    lines = data.strip().splitlines()
    return Transmission.from_ocr(lines)

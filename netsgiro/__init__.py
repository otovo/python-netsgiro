from typing import List

from netsgiro import enums, records


__version__ = '0.1.0'


# Nets' data sender/recipient ID
NETS_ID = '00008080'


def get_records(data: str) -> List[records.Record]:
    results = []

    for line in data.strip().splitlines():
        if len(line) != 80:
            raise ValueError('All lines must be exactly 80 chars long')

        record_type_str = line[6:8]
        if not record_type_str.isnumeric():
            raise ValueError(
                'Record type must be numeric, got {!r}'
                .format(record_type_str))

        record_type = enums.RecordType(int(record_type_str))
        record_cls = records.RECORD_CLASSES[record_type]

        results.append(record_cls.from_string(line))

    return results

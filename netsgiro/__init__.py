from typing import List

from netsgiro import enums, records


__version__ = '0.1.0'


# Nets' data sender/recipient ID
NETS_ID = '00008080'


def get_records(data: str) -> List[records.Record]:
    lines = data.strip().splitlines()

    for line in lines:
        if len(line) != 80:
            raise ValueError('All lines must be exactly 80 chars long')

    results = []

    for line in lines:
        record_type = enums.RecordType(int(line[6:8]))
        record_cls = records.RECORD_CLASSES[record_type]
        results.append(record_cls.from_string(line))

    return results

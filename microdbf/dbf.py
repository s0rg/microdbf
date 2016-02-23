import io

from .codepages import get_encoding
from .parsers import (
    DBFHeader,
    DBFField,
    FieldParser
)

def read_headers(stream, encoding):
    fields = []
    eo_hdr = frozenset([b'\r', b'\n', b''])

    # read
    while True:
        sep = stream.peek(1)[:1]
        if sep in eo_hdr:
            # End of field headers
            break

        field = DBFField.read(stream)
        field['type'] = ord(field['type'])
        field['name'] = field['name'].split(b'\0')[0].decode(encoding)
        fields.append((
            field['name'],
            field['length'],
            field['type'],
        ))

    # validate
    for n, l, t in fields:

        if t == 73 and l != 4:
            message = 'Field: `{}` of type I must have length 4 (was {})'
            raise ValueError(message.format(n, l))

        elif t == 76 and l != 1:
            message = 'Field: `{}` of type L must have length 1 (was {})'
            raise ValueError(message.format(n, l))

    return fields


def parse_dbf(fd_or_bytes, encoding=None):
    reader = io.BufferedReader(fd_or_bytes)

    header = DBFHeader.read(reader)

    encoding = encoding or \
               get_encoding(header['language_driver'])

    fields = read_headers(reader, encoding)

    reader.seek(header['headerlen'], io.SEEK_SET)

    read = reader.read
    seek = reader.seek

    parser = FieldParser(header['dbversion'], encoding)
    parse = parser.parse

    skip_len = header['recordlen'] - 1
    eo_rec = frozenset([b'\x1a', b''])

    while True:
        sep = read(1)

        if sep in eo_rec:
            break
        elif sep != b' ':
            seek(skip_len, io.SEEK_CUR)
            continue

        items = [
            (name, parse(ftype, read(length)))
            for name, length, ftype in fields
        ]

        yield dict(items)


import struct
import datetime
from decimal import Decimal


class StructParser(object):
    """
    Parser that converts (C style) binary structs named tuples.
    The struct can be read from a file or a byte string.
    """
    def __init__(self, fmt, names):
        self.names = names
        self.struct = struct.Struct(fmt)
        self.size = self.struct.size

    def unpack(self, data):
        """Unpack struct from binary string and return a dict."""
        s = self.struct
        return dict(zip(self.names, s.unpack(data)))

    def read(self, fd):
        """Read struct from a file-like object (implenting read())."""
        return self.unpack(fd.read(self.size))


# Pre-defined parsers

'''
For `dbversion` and `language_driver` possible values see:

    http://www.autopark.ru/ASBProgrammerGuide/DBFSTRUC.HTM
    http://www.clicketyclick.dk/databases/xbase/format/index.html

'''
DBFHeader = StructParser(
    '<BBBBLHHHBBLLLBBH',
    ['dbversion',
     'year',
     'month',
     'day',
     'numrecords',
     'headerlen',
     'recordlen',
     'reserved1',
     'incomplete_transaction',
     'encryption_flag',
     'free_record_thread',
     'reserved2',
     'reserved3',
     'mdx_flag',
     'language_driver',
     'reserved4',
     ]
)

DBFField = StructParser(
    '<11scLBBHBBBB7sB',
    ['name',
     'type',
     'address',
     'length',
     'decimal_count',
     'reserved1',
     'workarea_id',
     'reserved2',
     'reserved3',
     'set_fields_flag',
     'reserved4',
     'index_field_flag',
     ]
)


class FieldParser(object):
    def __init__(self, version, encoding):
        """Create a new field parser

        encoding is the character encoding to use when parsing
        strings."""
        self.dbversion = version
        self.encoding = encoding
        self._lookup = self._create_lookup_table()

    def _create_lookup_table(self):
        """Create a lookup table for field types."""
        lookup = {}

        for name in dir(self):
            if name.startswith('parse_'):
                fld_type = name[6:]
                if len(fld_type) == 2:
                    lookup[int(fld_type)] = getattr(self, name)

        return lookup

    def parse(self, field_type, data):
        """Parse field and return value"""
        fn = self._lookup.get(field_type, lambda d: d)
        return fn(data)

    def parse_48(self, data):
        """Parse flags field and return as byte string"""
        return data

    def parse_67(self, data):
        """Parse char field and return unicode string"""
        return str(data.rstrip(b'\0 '), self.encoding)

    def parse_68(self, data):
        """Parse date field and return datetime.date or None"""
        try:
            return datetime.date(int(data[:4]), int(data[4:6]), int(data[6:8]))
        except ValueError:
            if data.strip(b' 0') == b'':
                # A record containing only spaces and/or zeros is
                # a NULL value.
                return None
            raise ValueError('invalid date {!r}'.format(data))

    def parse_70(self, data):
        """Parse float field and return float or None"""
        if data.strip():
            return float(data)

    def parse_73(self, data):
        """Parse integer or autoincrement field and return int."""
        # Todo: is this 4 bytes on every platform?
        return struct.unpack('<i', data)[0]

    def parse_76(self, data):
        """Parse logical field and return True, False or None"""
        if data in b'TtYy':
            return True
        elif data in b'FfNn':
            return False
        elif data in b'? ':
            return None

        message = 'Illegal value for logical field: {!r}'
        raise ValueError(message.format(data))

    def parse_78(self, data):
        """Parse numeric field (N)

        Returns int, float or None if the field is empty.
        """
        try:
            return int(data)
        except ValueError:
            if data.strip():
                return float(data.replace(b',', b'.'))

    def parse_79(self, data):
        """Parse long field (O) and return float."""
        return struct.unpack('d', data)[0]

    def parse_84(self, data):
        """Parse time field (T)

        Returns datetime.datetime or None"""
        # Julian day (32-bit little endian)
        # Milliseconds since midnight (32-bit little endian)

        # Offset from julian days (used in the file) to proleptic Gregorian
        # ordinals (used by the datetime module)
        offset = 1721425  # Todo: check this out

        if data.strip():
            # Note: if the day number is 0, we return None
            # I've seen data where the day number is 0 and
            # msec is 2 or 4. I think we can safely return None for those.
            # (At least I hope so.)
            #
            day, msec = struct.unpack('<LL', data)
            if day:
                dt = datetime.datetime.fromordinal(day - offset)
                delta = datetime.timedelta(seconds=msec/1000)
                return dt + delta

    def parse_89(self, data):
        """Parse currency field (Y) and return decimal.Decimal.

        The field is encoded as a 8-byte little endian integer
        with 4 digits of precision."""
        value = struct.unpack('<q', data)[0]

        # Currency fields are stored with 4 points of precision
        return Decimal(value) / 10000

    def parse_66(self, data):
        """Binary memo field or double precision floating point number

        dBase uses B to represent a memo index (10 bytes), while
        Visual FoxPro uses it to store a double precision floating
        point number (8 bytes).
        """
        if self.dbversion in (0x30, 0x31, 0x32):
            return struct.unpack('d', data)[0]

    # Autoincrement field ('+')
    parse_43 = parse_73

    # Timestamp field ('@')
    parse_64 = parse_84


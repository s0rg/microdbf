import unittest
import datetime
from decimal import Decimal
from functools import partial

from microdbf.parsers import FieldParser


def build_mock(field_type, version=0x02, encoding='ascii'):
    p = FieldParser(version, encoding)
    return partial(p.parse, ord(field_type))


class TestFieldParser(unittest.TestCase):

    def test_0(self):
        '''Raw `0` field'''
        parse = build_mock('0')

        self.assertEqual(parse(b'\0'), b'\x00')
        self.assertEqual(parse(b'\xaa\xff'), b'\xaa\xff')

    def test_D(self):
        '''Date `D` field'''
        parse = build_mock('D')

        self.assertIsNone(parse(b'00000000'))
        self.assertIsNone(parse(b'        '))

        epoch = datetime.date(1970, 1, 1)
        self.assertEqual(parse(b'19700101'), epoch)

        with self.assertRaises(ValueError):
            parse(b'NotIntgr')

    def test_F(self):
        '''Float `F` field'''
        parse = build_mock('F')

        self.assertIsNone(parse(b''))
        self.assertIsNone(parse(b' '))

        self.assertEqual(parse(b'0'), 0)
        self.assertEqual(parse(b'1'), 1)
        self.assertEqual(parse(b'-1'), -1)
        self.assertEqual(parse(b'3.14'), 3.14)

        with self.assertRaises(ValueError):
            parse(b'jsdf')

    def test_I(self):
        '''Integer (`I`, `+`) fields'''
        # This also tests parse_43
        parse = build_mock('I')

        # Little endian unsigned integer.
        self.assertEqual(parse(b'\x00\x00\x00\x00'), 0)
        self.assertEqual(parse(b'\x01\x00\x00\x00'), 1)
        self.assertEqual(parse(b'\xff\xff\xff\xff'), -1)

    def test_N(self):
        '''Numeric `N` field'''
        parse = build_mock('N')

        self.assertIsNone(parse(b''))
        self.assertIsNone(parse(b' '))

        self.assertEqual(parse(b'1'), 1)
        self.assertEqual(parse(b'-99'), -99)
        self.assertEqual(parse(b'3.14'), 3.14)

        with self.assertRaises(ValueError):
            parse(b'okasd')

    def test_O(self):
        '''Double `O` field'''
        parse = build_mock('O')

        self.assertEqual(parse(b'\x00' * 8), 0.0)
        self.assertEqual(parse(b'\x00\x00\x00\x00\x00\x00\xf0?'), 1.0)
        self.assertEqual(parse(b'\x00\x00\x00\x00\x00\x00Y\xc0'), -100)

    def test_T(self):
        '''Time (`T`, `@`) fields'''
        # This also tests parse_64() (@)
        parse = build_mock('T')

        self.assertIsNone(parse(b''))
        self.assertIsNone(parse(b' '))

        # Todo: add more tests.

    def test_Y(self):
        '''Currency `Y` field'''
        parse = build_mock('Y')

        self.assertEqual(parse(b'\1\0\0\0\0\0\0\0'), Decimal('0.0001'))
        self.assertEqual(parse(b'\xff\xff\xff\xff\xff\xff\xff\xff'), Decimal('-0.0001'))

    def test_L(self):
        '''Logical `L` field'''
        parse = build_mock('L')

        for char in b'TtYy':
            self.assertTrue(parse(char))

        for char in b'FfNn':
            self.assertFalse(parse(char))

        for char in b'? ':
            self.assertIsNone(parse(char))

        # Some invalid values.
        for char in b'!0':
            with self.assertRaises(ValueError):
                parse(char)

    def test_B(self):
        '''Binary or Double `B` field'''
        # In VisualFox the B field is a double precision floating point number.
        parse = build_mock('B', version=0x30)

        self.assertIsInstance(parse(b'01abcdef'), float)
        self.assertEqual(parse(b'\0' * 8), 0.0)

        # Data must be exactly 8 bytes.
        with self.assertRaises(Exception):
            parse(b'')

        # In other db versions it is a memo index.

        parse = build_mock('B', version=0x02)

        self.assertIsNone(parse(b'1'))
        self.assertIsNone(parse(b''))

    def test_C(self):
        '''Character `C` field'''
        # ascii
        parse = build_mock('C')

        t = parse(b'test')
        self.assertIsInstance(t, str)
        self.assertEqual(t, 'test')

        test_str = 'Привет мир'

        for enc in ('cp1251', 'cp866'):
            parse = build_mock('C', encoding=enc)

            t = parse(test_str.encode(enc))

            self.assertIsInstance(t, str)
            self.assertEqual(t, test_str)


if __name__ == '__main__':
    unittest.main(verbosity=1)


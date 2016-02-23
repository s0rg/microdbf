__author__ = 'Alexey Shevchenko'
__email__ = 's0rg@ngs.ru'
__license__ = 'MIT'
__version__ = '1.0.0'


__doc__ = '''
from microdbf import parse_dbf

with open('some.dbf', 'rb') as fd:
    for record in parse_dbf(fd):
        print(record)

'''

from .dbf import parse_dbf

__all__ = [
    'parse_dbf',
]

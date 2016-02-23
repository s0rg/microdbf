# microdbf
Tiny pure python stream-oriented dbf reader

```python
from microdbf import parse_dbf

with open('some.dbf', 'rb') as fd:
    for record in parse_dbf(fd):
        print(record)

```
---
or
---

```python
from microdbf import parse_dbf

with open('some.dbf', 'rb') as fd:
    data = fd.read()
    for record in parse_dbf(data):
        print(record)

```

This project based on [dbfread](https://github.com/olemb/dbfread/) code

# Restrictions

* No memo-files handling (FPT and DBT)
* No deleted records handling

# License
-------

microdbf is released under the terms of the [MIT license](http://en.wikipedia.org/wiki/MIT_License>)


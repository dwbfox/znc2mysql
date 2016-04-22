# znc2mysql
This ZNC module provides support for logging messages into a MySQL database. It is currently in its early stages, with no support to generate the required database schema and requires manual configuration of the database information.


![znc2mysql](https://i.imgur.com/X15M9PO.png)
## requirements
This module requires:
* Python 3
* `pymysql` package
* `py-pretty` package
* Additionally (and obviously) [znc with modpython module enabled](http://wiki.znc.in/Modpython)


## setup
#### Set up the database
Create a new MySQL database, and run the included schema (`db.sql`) to create the required tables.

#### Configure database connection settings
open `znc2mysql.py` and edit the following to reflect your database settings:
```python
    self.connection = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        db='irc',
        cursorclass=pymysql.cursors.DictCursor
    )
```

#### Install the module
Move `znc2mysql.py` to your znc modules folder (typically `~/.znc/modules`)

#### Load the module in znc
`loadmod znc2mysql`


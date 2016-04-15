# znc2mysql
This ZNC module provides support for logging messages into a MySQL database. It is currently in its early stages, with no support to generate the required database schema and requires manual configuration of the database information.


![znc2mysql](https://i.imgur.com/X15M9PO.png)
## requirements
This module requires:
* Python 3
* pymysql package
* Additionally (and obviously) [znc with modpython module enabled](http://wiki.znc.in/Modpython)


## setup
#### Configure database connection settings
Open `settings.json` and fill in the MySQL connection info

#### Install the module
Move `znc2mysql.py` and `settings.json` to your znc modules folder (typically `~/.znc/modules`)

#### Load the module
`loadmod znc2mysql`


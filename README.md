# Erlample（Erlang Example）

An Erlang Example Repository


## Dependencies

- Python
- [Tornado](http://www.tornadoweb.org/) 
- [Psycopg](http://www.psycopg.org/psycopg/)
- PostgreSQL


## Launch Web Server

    python ./erlple.py
    
    
## Generate Erlang Example HTML

	python ./create_erlple.py


## Import erlample.sql

Create Database

    createdb erlample -O erlample -E UTF8 -e

Import erlample.sql to your database.

    psql -f erlample.sql
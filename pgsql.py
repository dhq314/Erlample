import os
import json
import psycopg2
import psycopg2.extras


class Pgsql:
    conn = None
    cursor = None

    def __init__(self):
        config_file = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_file, 'rb') as f:
        # f = open('config.json', 'rb')
            config = json.load(f)
        DB_NAME = config['db_name']
        DB_USER = config['db_user']
        DB_PASSWORD = config['db_password']
        DB_HOST = config['db_host']
        self.conn = psycopg2.connect(
            "dbname=" + DB_NAME + " user=" + DB_USER + " password=" + DB_PASSWORD + " host=" + DB_HOST)
        self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def __del__(self):
        if self.cursor is not None:
            self.cursor.close()
        if self.conn is not None:
            self.conn.close()

    def fetchone(self, sql):
        self.cursor.execute(sql)
        rs = self.cursor.fetchone()
        return rs

    def fetchall(self, sql):
        self.cursor.execute(sql)
        rs = self.cursor.fetchall()
        return rs

    def fetchnum(self, sql):
        rs = self.fetchall(sql)
        return len(rs)

    def query(self, sql):
        self.cursor.execute(sql)
        self.conn.commit()


import psycopg2
import psycopg2.extras

DB_NAME = "erlample"
DB_USER = "db_user"
DB_PASSWORD = "db_password"
DB_HOST = "127.0.0.1"


class Pgsql:
    conn = None
    cursor = None

    def __init__(self):
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


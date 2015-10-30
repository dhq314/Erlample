# -*- coding:utf-8 -*-
"""
PostgreSQL 数据库操作类
Created on 2013/05/23
@author: Joe Deng
@contact: dhq314@gmail.com
"""

import os
import json
import psycopg2
import psycopg2.extras


class Pgsql:
    conn = None
    cursor = None

    def __init__(self):
        config_file = os.path.join(os.path.dirname(__file__), 'config.json')
        # f = open('config.json', 'rb')
        with open(config_file, 'rb') as fp:
            config = json.load(fp)
        db_name = config['db_name']
        db_user = config['db_user']
        db_password = config['db_password']
        db_host = config['db_host']
        self.conn = psycopg2.connect(
            "dbname=" + db_name + " user=" + db_user + " password=" + db_password + " host=" + db_host)
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

    def fetch_num(self, sql):
        rs = self.fetchall(sql)
        return len(rs)

    def query(self, sql):
        self.cursor.execute(sql)
        self.conn.commit()

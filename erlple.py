# -*- coding: utf-8 -*-

#!/usr/bin/env python
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os.path
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.escape import json_encode

import pgsql

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        pg = pgsql.Pgsql()
        rs = pg.fetchall("SELECT * FROM mod")
        ms = []
        for r in rs:
            r['func_num'] = pg.fetchnum("SELECT id FROM funcs WHERE mid = " + str(r['id']))
            ms.append(r)
        self.render("mod_list.html", rs=ms)


class FunHandler(tornado.web.RequestHandler):
    def get(self, mid):
        condition = ""
        mflag = None
        if mid.isdigit():
            condition = "WHERE mid = " + str(mid)
            mflag = mid
        pg = pgsql.Pgsql()
        fs = pg.fetchall("SELECT id, name, mid, describe FROM funcs " + condition + " ORDER BY id DESC")
        i = len(fs)
        if i > 0:
            ms = pg.fetchall("SELECT id, name FROM mod ORDER BY name ASC")
            dms = {}
            for m in ms:
                dms[m['id']] = m['name']
            rs = []
            for f in fs:
                f['index'] = i
                if f['mid'] == 0 or f['mid'] == "0":
                    print f
                    mod_name = "no_mod_name"
                else:
                    mod_name = dms[f['mid']]
                url = "http://erlple/html/modules/" + mod_name + "/" + f['name'].replace("/",
                                                                                         "_") + ".html?search=" + mod_name + ":"
                f['mod_name'] = mod_name
                f['url'] = url
                rs.append(f)
                i = i - 1
        else:
            rs = None
        self.render("fun_list.html", rs=rs, mflag=mflag)


class FunActionHandler(tornado.web.RequestHandler):
    def get(self, action, fid):
        if action == "add":
            mflag = None
            if fid.isdigit():
                mflag = int(fid)
            rs = {}
            pg = pgsql.Pgsql()
            ms = pg.fetchall("SELECT id, name FROM mod")
            tms = []
            for m in ms:
                m['func_num'] = pg.fetchnum("SELECT id FROM funcs WHERE mid = " + str(m['id']))
                tms.append(m)
            rs['ms'] = tms
            rs['fs'] = None
            self.render("fun_action.html", ms=tms, fs=None, mflag=mflag, funname=None)
        elif action == "up":
            fid = fid.strip()
            if fid.isdigit():
                pg = pgsql.Pgsql()
                ms = pg.fetchall("SELECT id, name FROM mod")
                tms = []
                for m in ms:
                    m['func_num'] = pg.fetchnum("SELECT id FROM funcs WHERE mid = " + str(m['id']))
                    tms.append(m)
                fs = pg.fetchone("SELECT id, name, describe, usage, html, mid FROM funcs WHERE id = " + str(fid))
                self.render("fun_action.html", ms=tms, fs=fs, mflag=None, funname=None)
            else:
                self.redirect("/fun/")
        elif action == "del":
            fid = fid.strip()
            if fid.isdigit():
                sql = "DELETE FROM funcs WHERE id = " + str(fid)
                pg = pgsql.Pgsql()
                # pg.query(sql)
            self.redirect("/fun/")
        else:
            self.redirect("/fun/")

    def post(self, action, param):
        if action == "adding":
            mid = self.get_argument("mid", None)
            func_name = self.get_argument("func_name", None).replace("'", "`")
            func_html = self.get_argument("func_html", None).replace("'", "`")
            func_desc = self.get_argument("func_desc", None).replace("'", "`")
            func_usage = self.get_argument("func_usage", None).replace("'", "`")
            pg = pgsql.Pgsql()
            sql = "SELECT * FROM funcs WHERE mid = " + str(mid) + " and name = '" + func_name + "'"
            rs = pg.fetchone(sql)
            if not rs and mid.isdigit() and func_name and func_html:
                pg.query(
                    "INSERT INTO funcs(name, mid, html, describe, usage) values('" + func_name + "', " + mid + ", '" + func_html + "', '" + func_desc + "', '" + func_usage + "')")
        elif action == "updating":
            func_up(self)
        os.system("python /Users/dengjoe/erlang/erlple/create_erlple.py")
        self.redirect("/fun/")


class FunAction2Handler(tornado.web.RequestHandler):
    def get(self, action, mid, func_name):
        print func_name
        if action == "add":
            mflag = None
            if mid.isdigit():
                mflag = int(mid)
            rs = {}
            pg = pgsql.Pgsql()
            ms = pg.fetchall("SELECT id, name FROM mod")
            tms = []
            for m in ms:
                m['func_num'] = pg.fetchnum("SELECT id FROM funcs WHERE mid = " + str(m['id']))
                tms.append(m)
            rs['ms'] = tms
            rs['fs'] = None
            func_name = func_name.replace("-", "/")
            self.render("fun_action.html", ms=tms, fs=None, mflag=mflag, funname=func_name)


class ModActionHandler(tornado.web.RequestHandler):
    def get(self, action, mid):
        if action == "add":
            self.render("mod_action.html", rs=None)
        elif action == "del":
            mid = mid.strip()
            if mid.isdigit():
                sql = "DELETE FROM mod WHERE id = " + mid
                pg = pgsql.Pgsql()
                # pg.query(sql)
            self.redirect("/")
        elif action == "up":
            mid = mid.strip()
            if mid.isdigit():
                pg = pgsql.Pgsql()
                rs = pg.fetchone("SELECT * FROM mod WHERE id = " + str(mid))
                self.render("mod_action.html", rs=rs)
            else:
                self.redirect("/")
        elif action == "get_func_list":
            pg = pgsql.Pgsql()
            rs = pg.fetchall("SELECT name FROM funcs WHERE mid = " + str(mid))
            ret = ""
            for r in rs:
                ret = ret + r['name'] + ","
            ret = ret.strip(",")
            self.write(ret)
        elif action == "get_mod_list":
            ret = {}
            pg = pgsql.Pgsql()
            rs = pg.fetchall("SELECT id, name FROM mod")
            for r in rs:
                func_num = pg.fetchnum("SELECT id FROM funcs WHERE mid = " + str(r['id']))
                ret[r['id']] = {"name": r['name'], "func_num": func_num}
            self.write(json_encode(ret))

    def post(self, action, param):
        if action == "adding":
            mod_name = self.get_argument("mod_name", None).replace("'", "`")
            mod_desc = self.get_argument("mod_desc", None).replace("'", "`")
            if mod_name and mod_desc:
                mod_html = self.get_argument("mod_html", "").replace("'", "`")
                sql = "INSERT INTO mod(name, describe, html) values('" + mod_name + "', '" + mod_desc + "', '" + mod_html + "')"
                pg = pgsql.Pgsql()
                pg.query(sql)
        elif action == "updating":
            mid = self.get_argument("mid", None)
            mod_name = self.get_argument("mod_name", None).replace("'", "`")
            mod_desc = self.get_argument("mod_desc", None).replace("'", "`")
            if mid.isdigit() and mod_name and mod_desc:
                mod_html = self.get_argument("mod_html", "").replace("'", "`")
                sql = "UPDATE mod SET name = '" + mod_name + "', describe = '" + mod_desc + "', html = '" + mod_html + "' WHERE id = " + str(
                    mid)
                pg = pgsql.Pgsql()
                pg.query(sql)
        self.redirect("/")


def func_up(self):
    fid = self.get_argument("fid", None)
    mid = self.get_argument("mid", None)
    func_name = self.get_argument("func_name", None).replace("'", "`")
    func_html = self.get_argument("func_html", None).replace("'", "`")
    func_desc = self.get_argument("func_desc", None).replace("'", "`")
    func_usage = self.get_argument("func_usage", None).replace("'", "`")
    if fid.isdigit() and mid.isdigit() and func_name and func_html:
        pg = pgsql.Pgsql()
        pg.query(
            "UPDATE funcs SET name = '" + func_name + "', mid = " + mid + ", html = '" + func_html + "', describe = '" + func_desc + "', usage = '" + func_usage + "' WHERE id = " + fid)


def main():
    tornado.options.parse_command_line()
    handlers = [
        (r"/mod_action/(.+)/(.*)", ModActionHandler),
        (r"/mod", MainHandler),
        (r"/fun_action/(.+)/(.*)", FunActionHandler),
        (r"/fun_action2/(.+)/(.*)/(.*)", FunAction2Handler),
        (r"/fun/(.*)", FunHandler),
        (r"/", MainHandler)
    ]
    settings = dict(
        title=u"Erlample",
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static")
    )
    application = tornado.web.Application(handlers, debug=True, **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()

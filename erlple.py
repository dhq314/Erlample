#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Erlample 管理后台
Created on 2013/05/23
@author: Joe Deng
@contact: dhq314@gmail.com
"""

import os.path
import json
import urlparse
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.escape import json_encode

import pgsql


class MainHandler(tornado.web.RequestHandler):
    def get(self, cur_page):
        per_page = 20
        total_sql = "SELECT id FROM mod"
        cur_page, total_page, prev_page, next_page, start = page(cur_page, per_page, total_sql)

        pg = pgsql.Pgsql()
        ms = pg.fetchall("SELECT id, name, describe, html FROM mod LIMIT %d OFFSET %d" % (per_page, start))
        mod_list = []
        for m in ms:
            m['func_num'] = pg.fetch_num("SELECT id FROM funcs WHERE mid = %d" % m['id'])
            mod_list.append(m)
        template_variables = dict(
            mod_list=mod_list,
            cur_page=cur_page,
            total_page=total_page,
            prev_page=prev_page,
            next_page=next_page
        )
        self.render("mod_list.html", **template_variables)


class FunHandler(tornado.web.RequestHandler):
    def get(self, mid):
        condition = ""
        template_variables = {}
        current_mid = None
        if mid.isdigit():
            condition = "WHERE mid = %s" % mid
            current_mid = mid

        query_args = qs(self.request.uri)
        # if query_args['page']:
        #     cur_page = query_args['page']
        # else:
        #     cur_page = "1"
        cur_page = "1"
        print cur_page
        per_page = 30
        total_sql = "SELECT id FROM funcs %s" % condition
        cur_page, total_page, prev_page, next_page, start = page(cur_page, per_page, total_sql)

        pg = pgsql.Pgsql()
        fs = pg.fetchall("SELECT id, name, mid, describe FROM funcs %s ORDER BY id DESC LIMIT %d OFFSET %d" % (
            condition, per_page, start))

        i = len(fs)
        if i > 0:
            ms = pg.fetchall("SELECT id, name FROM mod ORDER BY name ASC")
            mod_name_dict = {}
            for m in ms:
                mod_name_dict[m['id']] = m['name']
            rs = []
            config_data = get_config_data()
            for f in fs:
                f['index'] = i
                if f['mid'] == 0 or f['mid'] == "0":
                    print f
                    mod_name = "no_mod_name"
                else:
                    mod_name = mod_name_dict[f['mid']]
                url = config_data['web_url'] + "modules/" + mod_name + "/" + \
                      f['name'].replace("/", "_") + ".html?search=" + mod_name + ":"
                f['mod_name'] = mod_name
                f['url'] = url
                rs.append(f)
                i -= 1
        else:
            rs = None
        template_variables['rs'] = rs
        template_variables['current_mid'] = current_mid
        self.render("fun_list.html", **template_variables)


class FunActionHandler(tornado.web.RequestHandler):
    def get(self, action, fid):
        if action == "add":
            current_mid = None
            if fid.isdigit():
                current_mid = int(fid)
            pg = pgsql.Pgsql()
            ms = pg.fetchall("SELECT id, name FROM mod")
            mod_list = []
            for m in ms:
                m['func_num'] = pg.fetch_num("SELECT id FROM funcs WHERE mid = %d" % m['id'])
                mod_list.append(m)
            template_variables = dict(
                ms=mod_list,
                fs=None,
                current_mid=current_mid,
                funname=None
            )
            self.render("fun_action.html", **template_variables)
        elif action == "up":
            fid = fid.strip()
            if fid.isdigit():
                pg = pgsql.Pgsql()
                ms = pg.fetchall("SELECT id, name FROM mod")
                mod_list = []
                for m in ms:
                    m['func_num'] = pg.fetch_num("SELECT id FROM funcs WHERE mid = %d" % m['id'])
                    mod_list.append(m)
                fs = pg.fetchone("SELECT id, name, describe, usage, html, mid FROM funcs WHERE id = %s" % fid)
                template_variables = dict(
                    ms=mod_list,
                    fs=fs,
                    current_mid=None,
                    funname=None
                )
                self.render("fun_action.html", **template_variables)
            else:
                self.redirect("/fun/")
        elif action == "del":
            # fid = fid.strip()
            # if fid.isdigit():
            #     sql = "DELETE FROM funcs WHERE id = " + str(fid)
            #     pg = pgsql.Pgsql()
            #     pg.query(sql)
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
                pg.query("INSERT INTO funcs(name, mid, html, describe, usage) values('" + func_name + "', " +
                         mid + ", '" + func_html + "', '" + func_desc + "', '" + func_usage + "')")
        elif action == "updating":
            fid = self.get_argument("fid", None)
            mid = self.get_argument("mid", None)
            func_name = self.get_argument("func_name", None).replace("'", "`")
            func_html = self.get_argument("func_html", None).replace("'", "`")
            func_desc = self.get_argument("func_desc", None).replace("'", "`")
            func_usage = self.get_argument("func_usage", None).replace("'", "`")
            if fid.isdigit() and mid.isdigit() and func_name and func_html:
                pg = pgsql.Pgsql()
                pg.query(
                    "UPDATE funcs SET name = '" + func_name + "', mid = " + mid + ", html = '" + func_html +
                    "', describe = '" + func_desc + "', usage = '" + func_usage + "' WHERE id = " + fid)
        create_erlple_file = os.path.join(os.path.dirname(__file__), 'create_erlple.py')
        os.system("python %s" % create_erlple_file)
        self.redirect("/fun/")


class FunAction2Handler(tornado.web.RequestHandler):
    def get(self, action, mid, func_name):
        # print func_name
        if action == "add":
            current_mid = None
            if mid.isdigit():
                current_mid = int(mid)
            pg = pgsql.Pgsql()
            ms = pg.fetchall("SELECT id, name FROM mod")
            mod_list = []
            for m in ms:
                m['func_num'] = pg.fetch_num("SELECT id FROM funcs WHERE mid = %d" % m['id'])
                mod_list.append(m)
            func_name = func_name.replace("-", "/")
            template_variables = dict(
                ms=mod_list,
                fs=None,
                current_mid=current_mid,
                funname=func_name
            )
            self.render("fun_action.html", **template_variables)


class ModActionHandler(tornado.web.RequestHandler):
    def get(self, action, mid):
        if action == "add":
            self.render("mod_action.html", rs=None)
        elif action == "del":
            # mid = mid.strip()
            # if mid.isdigit():
            #     sql = "DELETE FROM mod WHERE id = " + mid
            #     pg = pgsql.Pgsql()
            #     pg.query(sql)
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
                func_num = pg.fetch_num("SELECT id FROM funcs WHERE mid = " + str(r['id']))
                ret[r['id']] = {"name": r['name'], "func_num": func_num}
            self.write(json_encode(ret))

    def post(self, action, param):
        if action == "adding":
            mod_name = self.get_argument("mod_name", None).replace("'", "`")
            mod_desc = self.get_argument("mod_desc", None).replace("'", "`")
            if mod_name and mod_desc:
                mod_html = self.get_argument("mod_html", "").replace("'", "`")
                sql = "INSERT INTO mod(name, describe, html) values('" + mod_name + "', '" + \
                      mod_desc + "', '" + mod_html + "')"
                pg = pgsql.Pgsql()
                pg.query(sql)
        elif action == "updating":
            mid = self.get_argument("mid", None)
            mod_name = self.get_argument("mod_name", None).replace("'", "`")
            mod_desc = self.get_argument("mod_desc", None).replace("'", "`")
            if mid.isdigit() and mod_name and mod_desc:
                mod_html = self.get_argument("mod_html", "").replace("'", "`")
                sql = "UPDATE mod SET name = '" + mod_name + "', describe = '" + mod_desc + "', html = '" + \
                      mod_html + "' WHERE id = " + str(mid)
                pg = pgsql.Pgsql()
                pg.query(sql)
        self.redirect("/")


def get_config_data():
    """
    获取配置数据
    :return: config_data
    """
    config_file = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_file, 'rb') as fp:
        config_data = json.load(fp)
    return config_data


def page(cur_page, per_page, total_sql):
    """
    分页函数
    """
    pg = pgsql.Pgsql()
    total_num = pg.fetch_num(total_sql)
    total_page = ceil2(total_num, per_page)

    cur_page = cur_page.strip()
    if cur_page.isdigit():
        cur_page = int(cur_page)
        if cur_page < 1:
            cur_page = 1
    else:
        cur_page = 1
    prev_page = cur_page - 1
    if prev_page < 1:
        prev_page = 1
    next_page = cur_page + 1
    if next_page > total_page:
        next_page = total_page
    start = (cur_page - 1) * per_page

    return cur_page, total_page, prev_page, next_page, start


def ceil2(x, y):
    """
    Python2 的除数向上取整
    :param x: 除数
    :param y: 被除数
    :return: 向上取整的值
    """
    (div, mod) = divmod(x, y)
    if mod > 0:
        return div + 1
    else:
        return div


def qs(url):
    query = urlparse.urlparse(url).query
    return dict([(k, v[0]) for k, v in urlparse.parse_qs(query).items()])


if __name__ == "__main__":
    config = get_config_data()
    WEB_NAME = config['web_name']
    WEB_SERVER_LISTEN_PORT = config['web_server_listen_port']

    tornado.options.parse_command_line()
    handlers = [
        (r"/mod_action/(.+)/(.*)", ModActionHandler),
        (r"/mod/(.*)", MainHandler),
        (r"/mod(.*)", MainHandler),
        (r"/fun_action/(.+)/(.*)", FunActionHandler),
        (r"/fun_action2/(.+)/(.*)/(.*)", FunAction2Handler),
        (r"/fun/(.*)", FunHandler),
        (r"/(.*)", MainHandler)
    ]
    root_path = os.path.dirname(__file__)
    settings = dict(
        title=WEB_NAME,
        template_path=os.path.join(root_path, "templates"),
        static_path=os.path.join(root_path, "static")
    )
    application = tornado.web.Application(handlers, debug=True, **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(WEB_SERVER_LISTEN_PORT)
    print "%s Server Launched, Listen Port %d..." % (WEB_NAME, WEB_SERVER_LISTEN_PORT)
    tornado.ioloop.IOLoop.instance().start()

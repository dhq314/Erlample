# -*- coding: utf-8 -*-
"""
生成 Erlample 的显示页面
Created on 2013/05/27
@author: Joe Deng
@contact: dhq314@gmail.com
"""

import sys
import os
import json
import re
import tornado.template
import pgsql


def create_index(ms):
    content = tpl.load("index.html").generate(WEBNAME=WEB_NAME, WEBURL=WEB_URL, ACTURL=ACT_URL, ms=ms)
    save_file(PUB_DIR + "index.html", content)


def create_mod_list():
    content = tpl.load("mod_list.html").generate(WEBNAME=WEB_NAME, WEBURL=WEB_URL, ACTURL=ACT_URL)
    save_file(PUB_DIR + "mod_list.html", content)


def create_func_list():
    content = tpl.load("func_list.html").generate(WEBNAME=WEB_NAME, WEBURL=WEB_URL, ACTURL=ACT_URL)
    save_file(PUB_DIR + "func_list.html", content)


def create_erldocs_index(ms):
    content = ""
    content += "var index = [\n"
    mod_dict = {}
    for m in ms:
        mod_name = m['name']
        module_dir = MODULES_DIR + mod_name + "/"
        os.system("mkdir -p " + module_dir)
        create_module_template(m, module_dir)
        mod_dict[m['id']] = mod_name
        content += "\t['mod', '" + mod_name + "', '" + m['describe'] + "'],\n"

    fun_list = pg.fetchall(
        "SELECT funcs.* FROM funcs INNER JOIN mod ON funcs.mid = mod.id ORDER BY mod.name ASC, funcs.name ASC")
    regex = re.compile(r'(\[)(\w+?):(.*?)\/(\d+?)(\])')
    for fun in fun_list:
        mod_name = mod_dict[fun['mid']]
        module_dir = MODULES_DIR + mod_name + "/"
        html = fun['html'].replace("`", "'")
        html = re.sub(regex, '<a href="%smodules/\\2/\\3_\\4.html?search=\\2:">\\2:\\3/\\4</a>' % WEB_URL, html)
        desc = get_description(html)
        fun['mod_name'] = mod_name
        fun['desc'] = desc
        fun['html'] = html
        func_file_name = fun['name'].replace("/", "_")
        create_func_template(fun, module_dir, func_file_name)
        content += "\t['fun', '" + mod_name + "', '" + fun['name'] + "', '" + fun['describe'] + "'],\n"
    content += "];\n"
    save_file(PUB_DIR + "frontend/erldocs_index.js", content)


def create_module_template(m, module_dir):
    fs = pg.fetchall("SELECT * FROM funcs WHERE mid = %d ORDER BY name ASC" % m['id'])
    tfs = []
    for f in fs:
        f['fname'] = f['name'].replace("/", "_")
        tfs.append(f)
    content = tpl.load("mod.html").generate(WEBNAME=WEB_NAME, WEBURL=WEB_URL, ACTURL=ACT_URL, m=m, fs=tfs)
    if m['html']:
        content = unescape(content)
    save_file(module_dir + "index.html", content)


def create_func_template(f, module_dir, func_file_name):
    content = tpl.load("func.html").generate(WEBNAME=WEB_NAME, WEBURL=WEB_URL, ACTURL=ACT_URL, f=f)
    content = unescape(content)
    save_file(module_dir + func_file_name + ".html", content)


def get_description(html):
    desc = ""
    matches = re.findall(u"(\<p.*?\>)(.*?)(\<\/p\>)", html)
    for m in matches:
        d = m[1].strip()
        if d != "内部实现：":
            desc += d
    desc = strip_tags(desc)
    return substr(desc, 0, 500)


def substr(s, start, length=None):
    if len(s) < start or not length:
        return s[start:]
    elif length > 0:
        return s[start:start + length]
    else:
        return s[start:length]


def save_file(filename, content):
    fd = open(filename, "w")
    fd.write(content)
    fd.close()


def unescape(content):
    return content.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", "\"").replace("&amp;lt;", "<").replace(
        "&amp;gt;", ">")


def strip_tags(string):
    return re.sub(r'<[^>]*?>', '', string)


if __name__ == "__main__":
    if sys.getdefaultencoding() != 'gbk':
        reload(sys)
        sys.setdefaultencoding("utf-8")

    config_file = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_file, 'rb') as fp:
        config = json.load(fp)

    WEB_NAME = config['web_name']
    WEB_URL = config['web_url']
    ACT_URL = config['act_url']

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    PUB_DIR = BASE_DIR + "/public_html/"

    # 资源目录
    ASSETS_DIR = BASE_DIR + "/assets/"
    # 生成模块目录
    MODULES_DIR = PUB_DIR + "modules/"

    os.system("rm -rf " + PUB_DIR + "*")
    os.system("cp -r " + ASSETS_DIR + " " + PUB_DIR)
    os.system("mkdir -p " + MODULES_DIR)

    root_directory = os.path.join(os.path.dirname(__file__), "templates/create")
    tpl = tornado.template.Loader(root_directory)
    pg = pgsql.Pgsql()
    mod_list = pg.fetchall("SELECT * FROM mod ORDER BY name ASC")
    create_index(mod_list)
    create_mod_list()
    create_func_list()
    create_erldocs_index(mod_list)
    print "Generate %s HTML DONE!" % WEB_NAME

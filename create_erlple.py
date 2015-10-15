#encoding:utf-8
import os
import re
import sys
import tornado.template
import pgsql

from tornado.options import define

define("WEBNAME", default="Erlample（Erlang Example）")

WEBNAME = "Erlample（Erlang Example）"
ACTURL = "genserver.herokuapp.com"
# ACTURL = "localhost:8080"

BASE_DIR = "/Users/dengjoe/erlang/erlple/"
# 资源目录
ASSETS_DIR = BASE_DIR + "assets/"



if len(sys.argv) > 1:
    WEBURL = "http://dhq.me/erlample/"
    PUB_DIR = "/Users/dengjoe/beanstalk/zotonic/priv/sites/dhqme/erlample/"
else:
    WEBURL = "http://erlple/html/"
    PUB_DIR = BASE_DIR + "html/"

MODULES_DIR = PUB_DIR + "modules/"

os.system("rm -rf " + PUB_DIR + "*")
os.system("cp -r " + ASSETS_DIR + " " + PUB_DIR)
os.system("mkdir -p " + MODULES_DIR)

root_directory = os.path.join(os.path.dirname(__file__), "templates/create")
tpl = tornado.template.Loader(root_directory)
pg = pgsql.Pgsql()
ms = pg.fetchall("SELECT * FROM mod ORDER BY name ASC")


def main():
    create_index(ms)
    create_mod_list()
    create_func_list()
    create_erldocs_index(ms)


def create_index(ms):
    content = tpl.load("index.html").generate(WEBNAME=WEBNAME, WEBURL=WEBURL, ACTURL=ACTURL, ms=ms)
    save_file(PUB_DIR + "index.html", content)


def create_mod_list():
    content = tpl.load("mod_list.html").generate(WEBNAME=WEBNAME, WEBURL=WEBURL, ACTURL=ACTURL)
    save_file(PUB_DIR + "mod_list.html", content)


def create_func_list():
    content = tpl.load("func_list.html").generate(WEBNAME=WEBNAME, WEBURL=WEBURL, ACTURL=ACTURL)
    save_file(PUB_DIR + "func_list.html", content)


def create_erldocs_index(ms):
    content = ""
    content += "var index = [\n"
    MS = {}
    for m in ms:
        mod_name = m['name']
        module_dir = MODULES_DIR + mod_name + "/"
        os.system("mkdir -p " + module_dir)
        create_module_template(m, module_dir)
        MS[m['id']] = mod_name
        content += "\t['mod', '" + mod_name + "', '" + m['describe'] + "'],\n"

    fs = pg.fetchall(
        "SELECT funcs.* FROM funcs INNER JOIN mod ON funcs.mid = mod.id ORDER BY mod.name ASC, funcs.name ASC")
    regex = re.compile(r'(\[)(\w+?):(.*?)\/(\d+?)(\])')
    for f in fs:
        mod_name = MS[f['mid']]
        module_dir = MODULES_DIR + mod_name + "/"
        html = f['html'].replace("`", "'")
        html = re.sub(regex, '<a href="' + WEBURL + 'modules/\\2/\\3_\\4.html?search=\\2:">\\2:\\3/\\4</a>', html)
        desc = get_description(html)
        f['mod_name'] = mod_name
        f['desc'] = desc
        f['html'] = html
        func_file_name = f['name'].replace("/", "_")
        create_func_template(f, module_dir, func_file_name)
        content += "\t['fun', '" + mod_name + "', '" + f['name'] + "', '" + f['describe'] + "'],\n"
    content += "];\n"
    save_file(PUB_DIR + "frontend/erldocs_index.js", content)


def create_module_template(m, module_dir):
    fs = pg.fetchall("SELECT * FROM funcs WHERE mid = " + str(m['id']) + " ORDER BY name ASC")
    tfs = []
    for f in fs:
        f['fname'] = f['name'].replace("/", "_")
        tfs.append(f)
    content = tpl.load("mod.html").generate(WEBNAME=WEBNAME, WEBURL=WEBURL, ACTURL=ACTURL, m=m, fs=tfs)
    if m['html']:
        content = unescape(content)
    save_file(module_dir + "index.html", content)


def create_func_template(f, module_dir, func_file_name):
    content = tpl.load("func.html").generate(WEBNAME=WEBNAME, WEBURL=WEBURL, ACTURL=ACTURL, f=f)
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


def strip_tags(str):
    return re.sub(r'<[^>]*?>', '', str)


if __name__ == "__main__":
    main()

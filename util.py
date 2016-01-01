# -*- coding:utf-8 -*-
"""
工具函数
Created on 2015/11/27
@author: Joe Deng
@contact: dhq314@gmail.com
"""

import urlparse
import pgsql


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


def parse_qs(url):
    """
    获取 URL 参数
    :return: dict
    """
    query = urlparse.urlparse(url).query
    return dict([(k, v[0]) for k, v in urlparse.parse_qs(query).items()])


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
    offset = (cur_page - 1) * per_page

    return cur_page, total_page, prev_page, next_page, offset

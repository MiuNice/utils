# coding:utf-8

__version__ = "0.1.1"
__author__ = "wangyuhang"

import time
import json
import datetime


class TypeConversion(object):
    def __init__(self, value):
        self.value = value

        self.mapping = {
            "int": int,
            "float": float,
            "json_loads": json.loads
        }

    def int(self, default=0):
        assert isinstance(default, int), "默认值类型错误"
        return self.conversion("int", default)

    def float(self, default=0.0):
        assert isinstance(default, float), "默认值类型错误"
        return self.conversion("float", default)

    def json_loads(self, default=None):
        if not isinstance(default, dict):
            default = {}

        return self.conversion("json_loads", default)

    def conversion(self, _type, default):
        func = self.mapping.get(_type)
        if func is None:
            return default

        result = default
        try:
            result = func(self.value)
        except (ValueError, TypeError):
            pass
        finally:
            return result


def to(value):
    return TypeConversion(value)


def two_d_tuple2dict(_2d_tuple):
    _dict = dict()
    if isinstance(_2d_tuple, tuple):
        for row in _2d_tuple:
            if isinstance(row, tuple) and len(row) == 2:
                _dict[row[0]] = row[1]
    return _dict


def dt2ts(dt):
    if not dt:
        return 0
    return int(dt2ts_ms(dt) / 1000)


def dt2ts_ms(dt):
    if not dt:
        return 0
    return int(time.mktime(dt.timetuple()) * 1000)


def dict2list(_dict, keys=None):
    """
    将字典转换为列表嵌套字典的格式
    {k:v,k2,v2} -> [{key: k, "value: v}, {key: k2, value: v2}]
    """
    if keys is None or not isinstance(keys, (list, tuple)) or len(keys) != 2:
        keys = ("key", "value")

    k, v = keys

    result = list()
    for key, value in _dict.items():
        result.append({
            k: key, v: value
        })

    return result


def valid_date_format(date_string, format_string, default=None, return_dt=False):
    try:
        dt = datetime.datetime.strptime(date_string, format_string)
        return date_string if return_dt is False else dt
    except (ValueError, TypeError):
        if default is not None:
            return default
        dt = datetime.datetime.now()
        return dt.strftime(format_string) if return_dt is False else dt


def datetime_strftime(dt, format_string, default=None):
    try:
        return dt.strftime(format_string)
    except:
        if default is not None:
            return default
        return datetime.datetime.now().strftime(format_string)

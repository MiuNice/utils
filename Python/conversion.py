# coding:utf-8

__version__ = "0.2.0"
__author__ = "wangyuhang"

import time
import json
import datetime


class TypeConversionBase:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return json.dumps(self.value)

    def int(self, default=0):
        return TypeConversionInt(self.value, default)

    def float(self, default=0.0):
        return TypeConversionFloat(self.value, default)

    def json_load(self, default=None):
        return TypeConversionJsonLoads(self.value, default)

    def dict(self, default=None):
        return TypeConversionDict(self.value, default)


class TypeConversionInt(TypeConversionBase, int):
    def __new__(cls, value, default=0):
        try:
            value = int(value)
        except (ValueError, TypeError):
            value = default
        return super().__new__(cls, value)

    def __init__(self, value, default=0):
        super().__init__(value)


class TypeConversionFloat(TypeConversionBase, float):
    def __new__(cls, value, default=0.0):
        try:
            value = float(value)
        except (ValueError, TypeError):
            value = default
        return super().__new__(cls, value)

    def __init__(self, value, default=0.0):
        super().__init__(value)


class TypeConversionJsonLoads(TypeConversionBase):
    def __init__(self, value, default=None):
        try:
            value = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            value = default if default is not None else {}
        super().__init__(value)


class TypeConversionDict(TypeConversionBase):
    def __init__(self, value, default=None):
        if not isinstance(value, dict):
            value = default if default is not None else {}
        super().__init__(value)

    def get(self, key, default=None):
        return TypeConversionBase(self.value.get(key, default))


def to(value):
    return TypeConversionBase(value)


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

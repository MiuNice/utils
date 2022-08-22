def some_key2one_value(_set_key_list, _set_value):
    """
    : 用于将多个Key设置为同一个值
    """
    _dict = dict()
    for item in _set_key_list:
        _dict[item] = _set_value
    return _dict

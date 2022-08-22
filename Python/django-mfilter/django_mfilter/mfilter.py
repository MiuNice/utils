import copy
from collections import deque


class MField:
    def __init__(self, field, parent=None):
        self.name = field.name
        self.model = field.model
        self.parent = parent
        self.class_name = field.__class__.__name__
        self.related_model = field.related_model
        self.django_field = field


class MFields(object):
    def __init__(self, model):
        self.fields = list()
        self.fk_fields = list()

        self.model = model

        self.models = list()
        self.binding_memo = dict()
        self.__binding(model)
        self.map = self.__map()

    def __getitem__(self, index):
        return list(self.map.keys())[index]

    def __binding(self, _field):
        parent = None
        field_array = self.model_field(_field)
        fk_array = deque()

        while True:
            if not field_array and not fk_array:
                break

            for field in field_array:
                mfield = MField(field, parent)
                if mfield.class_name == "ForeignKey":
                    self.fields.append(mfield)
                    fk_array.append((mfield, self.model_field(mfield.related_model)))
                else:
                    if parent:
                        self.fk_fields.append(mfield)
                    else:
                        self.fields.append(mfield)

            new_field_array = None
            if fk_array:
                parent, new_field_array = fk_array.pop()
            field_array = new_field_array

    def __map(self):
        _fields, _fk_fields = self.fields, self.fk_fields
        _map = dict()
        _map.update({field.name: field for field in self.fields})
        _map.update({self.get_foreign_key(field): field for field in self.fk_fields})
        return _map

    @staticmethod
    def get_foreign_key(field):
        _field = field
        field_name_list = list()
        while True:
            field_name_list.append(_field.name)
            if _field.parent is None:
                break
            _field = _field.parent
        return "_".join(field_name_list[::-1])

    def get_mfield(self, field_name):
        return self.map.get(field_name)

    def is_foreign_key(self, field_name):
        mfield = self.get_mfield(field_name)
        if mfield.parent:
            return True
        return False

    def is_model_key(self, field_name):
        mfield = self.get_mfield(field_name)
        if mfield.parent is None:
            return True
        return False

    @staticmethod
    def model_field(model):
        return model._meta.fields


class XFilter:
    pass


class MFilter(XFilter):
    def __init__(self, request, model, params=dict()):
        self.model = model
        self.params = params
        if params:
            self.params = params
        else:
            self.params = self.request_params(request)

        self.funcs = dict()
        self.rename = dict()
        self.operate = dict()

        self.fields = MFields(model)

    @staticmethod
    def do_nothing(value):
        return value

    @staticmethod
    def request_params(request):
        http_params = dict()

        method = request.method
        if method == "GET":
            # django.http.request.QueryDict
            http_params = request.GET

        return http_params

    def _rename(self):
        new_name = dict()
        if self.rename:
            for key, value in self.params.items():
                if key in self.rename:
                    key = self.rename[key]
                new_name[key] = value
            self.params = new_name

    def _get_operate(self, key):
        return self.operate.get(key, "")

    def filter_params(self):
        if not self.params:
            return dict()

        self._rename()

        _filter_params = dict()
        for key, value in self.params.items():
            if key in self.fields:
                value = self.funcs.get(key, self.do_nothing)(value)
                if self.fields.is_foreign_key(key):
                    key = key.replace("_", "__")
                _filter_params[key + self._get_operate(key)] = value
        return _filter_params

    # set 函数未来可能更加饱满，现（在）不封装
    def set_funcs(self, *args, **kwargs):
        if args:
            self.funcs = args[0]
        else:
            self.funcs = kwargs
        return self

    def set_rename(self, *args, **kwargs):
        if args:
            self.rename = args[0]
        else:
            self.rename = kwargs
        return self

    def set_operate(self, *args, **kwargs):
        if args:
            self.operate = args[0]
        else:
            self.operate = kwargs
        return self

    def get_field(self, field):
        return self.fields[field]


### Django MFilter

用于给QuerySet提供查询条件



#### 快速开始

```python
# django View
from models import Test
from django_mfliter.mfilter import MFilter

def t_list(request):
    params = MFilter(request, Test).filter_params()
    queryset = Test.objects.filter(**params)


# modles.py
from django.db import models

class Test(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="id")
    created = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name="c")
    a = models.CharField(max_length=16, default="", null=False, verbose_name="a")
    b = models.CharField(max_length=16, default="", null=False, verbose_name="b")
```

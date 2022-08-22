### Django MLogger

基于Django（3.1及以上）的日志管理系统，通过配置Settings使用。

#### 快速开始
```python
from django_mlogger.mlogger import MLogger

m_logger = MLogger(__name__, "test")


@m_logger.guard()
def test():
    pass

```


### 日志

> logger主要用于每次调用情况的记录，可以自定义方式。

##### 使用
初始化client的时候可以传入debug参数。  
debug is True，会打印请求流程中的日志，包括接受请求，重试，收到响应等  
debug is False，只有在触发ERROR时会打印相关日志


默认formatter：
```
'%(asctime)s %(process)d %(thread)d %(levelname)s %(message)s'
```
默认handler
```
logging.StreamHandler()
```

自定义handler及formatter
```python
import os
import logging

from wulaisdk.client import WulaiClient

pubkey = os.getenv("PUBKEY", "")
secret = os.getenv("SECRET", "")
log_dir_path = "your_path"

client = WulaiClient(pubkey, secret, debug=True)

# eg: FileHandler
handler = logging.FileHandler(log_dir_path + '/logs/wulaisdk.log')
formatter = logging.Formatter('%(levelname)s %(message)s')
handler.setFormatter(formatter)
client.add_logger_handler(handler)
```
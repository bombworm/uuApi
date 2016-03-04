# uuApi
a Python implements of uuwise api
uuwise.com(优优云)的python客户端，recognize函数里的code_type参数参见：http://www.uuwise.com/price.html

##Example
```
api = uuApi("soft_id", "soft_key", "user_name", "user_password")
if api.enable():
    print api.recognize("captcha.jpg", 1004)
```

## Licence

See to [LICENSE](LICENSE) file。

# 12306 Script

自用的 12306 抢票脚本。

## 使用方法

1. 安装依赖

```bash
pip install -r requirements.txt
```

安装完 Python 依赖后，还需要安装 Chrome 浏览器和对应版本的 ChromeDriver。


2. 修改配置

```bash
cp conf.py.example conf.py
```

修改 `conf.py` 文件，填入乘车人信息、出发地、目的地、出发日期等信息。

3. 使用

运行后会打开浏览器，请使用手机扫码登录。

之后按照提示操作，到时间会自动抢票。

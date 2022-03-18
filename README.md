# QQ扫码登录部署脚本

代码包：

```
bk-qq-login
|-- add_settings_production.py  # 包含变量占位符，这部分内容会在部署脚本是自动加到settings_production.py里，覆盖default.py中的变量
|-- deploy.sh                   # 部署脚本，会将代码中的变量占位符用env.sh中的变量替换，并所有的代码文件同步到open_paas/login目录下
|-- ee_login                    # 配置QQ登录代码
|   |-- __init__.py
|   `-- settings_login.py
|-- ee_official_login           # 登录代码
|   |-- __init__.py
|   `-- qrcode
|       |-- __init__.py
|       `-- qq
|           |-- __init__.py
|           |-- backends.py
|           |-- settings.py     # 包含变量占位符
|           |-- utils.py
|           `-- views.py
|-- env.sh                      # 变量
|-- README.md                   # README.md
└── templates
    └── account
        ├── agreement.part      # 协议文件，无需关心
        └── login_ce_qq.html    # 前端模板文件
```

## 部署

在**paas部署好**后，在paas机器上任意路径下载代码包，解压，进入根目录，编辑env.sh文件，将以下所需变量补全

```
# 要启用QQ登录视图，需要设置QQ_LOGIN为True
QQ_LOGIN='True'

# QQ应用APP_ID
APP_ID=''

# QQ应用APP_KEY
APP_KEY=''

# redirect uri
REDIRECT_URI=''
```

执行部署脚本（需在paas机器上执行）：

```
chmod +x ./deploy.sh
./deploy.sh
```
 

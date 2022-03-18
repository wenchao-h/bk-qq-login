# 下述内容放置在open_paas/login/conf/settings_production.py文件内DEBUG = False之后
# 要启用QQ登录视图，需要设置QQ_LOGIN为True，同时在ee_login.settings_login设置自定义登录
QQ_LOGIN= __QQ_LOGIN__

CUSTOM_AUTHENTICATION_BACKEND = ""
try:
    custom_conf_module_path = "ee_login.settings_login"

    custom_conf_module = __import__(custom_conf_module_path, globals(), locals(), ["*"])
    LOGIN_TYPE = getattr(custom_conf_module, "LOGIN_TYPE", "bk_login")

    CUSTOM_LOGIN_VIEW = getattr(custom_conf_module, "CUSTOM_LOGIN_VIEW", "")
    CUSTOM_AUTHENTICATION_BACKEND = getattr(custom_conf_module, "CUSTOM_AUTHENTICATION_BACKEND", "")
except ImportError, e:
    print "load custom_login settings fail!", e
    LOGIN_TYPE = "bk_login"

AUTHENTICATION_BACKENDS_DICT = {
    "bk_login": ["backends.bk.BkUserBackend"],
    "custom_login": [CUSTOM_AUTHENTICATION_BACKEND],
}
if QQ_LOGIN:
    AUTHENTICATION_BACKENDS_DICT = {
        "bk_login": ["backends.bk.BkUserBackend"],
        "custom_login": [CUSTOM_AUTHENTICATION_BACKEND, "backends.bk.BkUserBackend"],
    }
AUTHENTICATION_BACKENDS = AUTHENTICATION_BACKENDS_DICT.get(LOGIN_TYPE, ["bkaccount.backends.BkRemoteUserBackend"])
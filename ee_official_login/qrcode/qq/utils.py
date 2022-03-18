# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS
Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import random, urllib
import requests
from django.conf import settings

from common.log import logger
from components.usermgr_api import _call_usermgr_api
from components.http import http_get
from . import settings as qq_settings

def get_qq_access_token(code):
    """
    获取qq access_token
    """
    token_url = qq_settings.ACCESS_TOKEN_URL.format(app_id=qq_settings.APP_ID, app_key=qq_settings.APP_KEY, code=code, redirect_uri=qq_settings.REDIRECT_URI)
    resp = requests.get(token_url)
    if resp.status_code != 200:
        # 记录错误日志
        content = resp.content[:100] if resp.content else ''
        logger.error("http enterprise request error! type: %s, url: %s, response_status_code: %s, response_content: %s", 'GET', token_url, resp.status_code, content)
        return None
    try:
        data = resp.json()
        logger.debug("response data is {}".format(data))
        access_token = data.get('access_token', None)
        return access_token
    except requests.exceptions.JSONDecodeError as e: 
        logger.exception("get qq access_token error: {}".format(str(e)))
        return None

def get_qq_user_info(access_token):
    """
    获取qq访问用户身份
    """
    info_url = qq_settings.QQ_USER_INFO_URL.format(access_token=access_token)

    info_resp = requests.get(info_url)
    if info_resp.status_code != 200:
        # 记录错误日志
        content = info_resp.content[:100] if info_resp.content else ''
        logger.error("http enterprise request error! type: %s, url: %s, response_status_code: %s, response_content: %s", 'GET', info_url, info_resp.status_code, content)
        return None
    try:
        info_data = info_resp.json()
        logger.debug("response data is {}".format(info_data))
        # 将企业微信的UserId字段映射为蓝鲸用户管理的username
        openid = info_data.get('openid', '')
        data = {
            "openid": openid
        }
        return data
    except requests.exceptions.JSONDecodeError as e: 
        logger.exception("get qq user info error: {}".format(str(e)))
        return None
    
def usermgr_get_user_v2(openid):
    """
    使用用户管理v2版本接口通过openid获取用户信息
    openid: qq openid
    """
    BK_USERMGR_HOST = "%s://%s" % ("http", settings.BK_USERMGR_HOST)
    url = "{host}/api/v2/profiles/{openid}/".format(host=BK_USERMGR_HOST, openid=openid)
    data = {
        "fields": "username",
        "lookup_field": "code"  # lookup_field为code
    }
    ok, code, message, _data = _call_usermgr_api(http_get, url, data)

    return ok, code, message, _data


def gen_oauth_state_security_token(length=32):
    """
    生成随机的state，防止csrf
    """
    allowed_chars = "abcdefghijkmnpqrstuvwxyzABCDEFGHIJKLMNPQRSTUVWXYZ0123456789"
    state = "".join(random.choice(allowed_chars) for _ in range(length))
    return state


def gen_oauth_login_url(extra_param):
    """
    生成跳转登录的URL
    """
    # 由于qq校验redirect_uri是精准匹配的，所有redirect_uri中无法带参数，只能放置在state中处理
    extra_param = {} if extra_param is None or not isinstance(extra_param, dict) else extra_param
    extra_param["security_token"] = gen_oauth_state_security_token()
    state = "&".join(["%s=%s" % (k, v) for k, v in extra_param.items() if v is not None and v != ""])
    # 跳转到 qq 登录的URL
    qq_oauth_login_url = "%s?%s" % (
        qq_settings.QQ_OAUTH2_URL,
        urllib.urlencode(
            {
                "response_type": "code",
                "client_id": qq_settings.APP_ID,
                "redirect_uri": qq_settings.REDIRECT_URI,
                "state": state,
            }
        ),
    )
    return qq_oauth_login_url, state
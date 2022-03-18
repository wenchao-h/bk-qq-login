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

import urlparse

from django.contrib.auth import authenticate
from django.template.response import TemplateResponse
from django.utils.translation import ugettext as _


from bkauth.constants import REDIRECT_FIELD_NAME
from bkauth import actions
from bkauth.forms import BkAuthenticationForm
from bkauth.utils import set_bk_token_invalid
from common.log import logger
from common.exceptions import AuthenticationError

from .utils import gen_oauth_login_url

def login(request):
    """
    登录处理
    """

    template_name = "account/login_ce_qq.html"

    # QQ登录回调后会自动添加code参数
    code = request.GET.get('code', None)

    # GET 请求中query param携带code，认为是QQ登录回调后的请求
    if code and request.method == "GET":
        return _qq_login(request=request,
            code=code,
            template_name=template_name,
            )
    else:
        # 蓝鲸账号密码登录由_bk_login处理
        return _bk_login(request=request, 
            authentication_form=BkAuthenticationForm, 
            template_name=template_name
            )

def _bk_login(request, authentication_form, template_name):
    """
    处理蓝鲸账号密码登录页面和登录动作：
    """

    error_message = ""

    # 获取用户实际请求的URL, 目前account.REDIRECT_FIELD_NAME = 'c_url'
    redirect_to = request.GET.get(REDIRECT_FIELD_NAME, '')
    # 获取用户实际访问的蓝鲸应用
    app_id = request.POST.get("app_id", request.GET.get("app_id", ""))

    # POST
    if request.method == "POST":
        form = authentication_form(request, data=request.POST)
        try:
            if form.is_valid():
                logger.info("_bk_login user: %s"%request.POST['username'])
                return actions.login_success_response(request, form, redirect_to, app_id)
        except AuthenticationError as e:
            error_message = e.message
        else:
            error_message = _(u"账户或者密码错误，请重新输入")
    else:
        form = authentication_form(request)

    qq_auth_url, state = gen_oauth_login_url({
        "c_url": redirect_to,
        "app_id": app_id
    })
    logger.debug("qq_auth_url is {}".format(qq_auth_url))
    logger.debug("state is {}".format(state))

    context = {
        "form": form,
        "error_message": error_message,
        REDIRECT_FIELD_NAME: redirect_to,
        "app_id": app_id,
        "is_plain": request.path_info == "/plain/",
        "qq_auth_url": qq_auth_url
    }
    request.session["state"] = state
    response = TemplateResponse(request, template_name, context)
    response = set_bk_token_invalid(request, response)
    return response

def _qq_login(request, code, template_name):

    state = request.GET.get("state", "")
    state_dict = dict(urlparse.parse_qsl(state))
    app_id = state_dict.get("app_id")
    redirect_to = state_dict.get(REDIRECT_FIELD_NAME, "")
    qq_auth_url, new_state = gen_oauth_login_url({
        "c_url": redirect_to,
        "app_id": app_id
    })
    logger.debug("qq_auth_url is {}".format(qq_auth_url))
    logger.debug("new_state is {}".format(new_state))

    error_message = ""
    context = {
        "error_message": error_message,
        REDIRECT_FIELD_NAME: redirect_to,
        "app_id": app_id,
        "is_plain": request.path_info == "/plain/",
        "qq_auth_url": qq_auth_url
    }

    state = request.GET.get("state", "")
    state_from_session = request.session.get("state", "")

    # 校验state，防止csrf攻击
    if state != state_from_session:
        error_message = u"state校验失败，请重新登录或联系管理员"
        logger.debug(
            "custom_login:qrcode.qq state != state_from_session [state=%s, state_from_session=%s]",
            state,
            state_from_session,
        )

        context["error_message"] = error_message
        return _qq_login_failed_response(request=request,
            template_name=template_name,
            context=context,
            state=new_state)

    user = authenticate(code=code)
    if user is None:
        error_message = u"qq用户不存在"
        logger.debug("custom_login: qrcode.qq user is None")
        context["error_message"] = error_message
        return _qq_login_failed_response(request=request,
            template_name=template_name,
            context=context,
            state=new_state)

    # 成功，则调用蓝鲸登录成功的处理函数，并返回响应
    logger.info("_qq_login user: %s"%user)
    logger.debug("custom_login:qrcode.qq login success, will redirect_to=%s", redirect_to)
    return actions.login_success_response(request, user, redirect_to, app_id)
    
def _qq_login_failed_response(request, template_name, context, state):
    """
    qq登录失败响应
    """
    request.session["state"] = state
    response = TemplateResponse(request, template_name, context)
    response = set_bk_token_invalid(request, response)
    return response

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

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

from common.log import logger
from .utils import get_qq_access_token, get_qq_user_info, usermgr_get_user_v2

class QQBackend(ModelBackend):
    """
    QQ二维码认证方法
    """
    def authenticate(self, code=None):
        # QQ登录验证
        try:
            # 调用接口验证登录票据CODE，并获取access_token
            access_token = get_qq_access_token(code)
            if not access_token:
                return None
            # 通过access_token 获取qq用户信息
            userinfo = get_qq_user_info(access_token)
            if not userinfo:
                logger.info("QQBackend get_qq_user_info fail")
                return None
            # 验证通过
            
            # 验证通过, username为qq openid
            openid = userinfo.get("openid")

            # 获取User类
            UserModel = get_user_model()

            # 业务代码，不具有参考价值，业务本身在用户管理已经保存了用户的QQ和openid信息，qq oauth认证已经不允许开发者获取用户请求信息了，只能拿到openid信息，这里是通过openid拿到对应的用户信息
            ok, _, message, data = usermgr_get_user_v2(openid) 
            logger.debug("data is {}".format(data))
            if ok:
                # 获取User类
                username = data.get('username', '')
                UserModel = get_user_model()
                user, _ = UserModel.objects.get_or_create(username=username)
                return user
            else:
                logger.info('usermgr_get_user_v2 failed, %s'%message)
                return None

        except Exception:
            logger.exception("qq qrcode login backend validation error!")
        return None

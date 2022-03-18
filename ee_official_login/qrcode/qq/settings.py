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

# app id
APP_ID = '__APP_ID__'

# app key
APP_KEY = '__APP_KEY__'

# redirect uri
REDIRECT_URI = '__REDIRECT_URI__'

# 获取access_token链接
ACCESS_TOKEN_URL = 'https://graph.qq.com/oauth2.0/token?grant_type=authorization_code&client_id={app_id}&client_secret={app_key}&code={code}&redirect_uri={redirect_uri}&fmt=json'

# oauth2 url
QQ_OAUTH2_URL = 'https://graph.qq.com/oauth2.0/authorize'

# 获取用户信息
QQ_USER_INFO_URL = 'https://graph.qq.com/oauth2.0/me?access_token={access_token}&fmt=json'

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
from utils import encode_token



def __get_request_token(user):
    payload = {
        "username": user.username,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "full_name": user.full_name,
        "sex": user.sex,
        "time": time.time(),
        "id": user.id
    }

    token = encode_token(payload)

    result = {
        "success": True,
        "code": 200,
        "message": u"登录成功",
        "token": token,
        # "token": 'Token {}'.format(token.key),
        "details": payload
    }
    return result


def login_view(request):
    params = request.data
    username = params.get("username")
    password = params.get("password")
    user = authenticate(username=username, password=password)

    if not user:
        result = {
            "success": False,
            "message": "用户名或者密码不正确",
            "code": 401
        }
    elif user and user.is_active:
        login(request, user)
        # token = Token.objects.create(user=user)
        result = __get_request_token(user)
    else:
        result = {
            "success": user.is_active,
            "code": user.error_code,
            "message": user.error_msg,
        }

    return result


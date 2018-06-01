#!usr/bin/env python  
# -*- coding:utf-8 _*-
# @author:fang
# @file: utils.py
# @time: 2018/4/8/11:07
# @Software: PyCharm
# @Describe:

AUTH_SECRET = "fXy@2018#12Yx.waj213@aggvn"

from itertools import chain
from datetime import datetime
from django.core.exceptions import PermissionDenied
from rest_framework.response import Response
from base.models.user import User
import jwt
from pytz import timezone
from django.db import models


def authorization(func):
    def wrapper(request, *args, **kwargs):
        token = request.META.get("HTTP_AUTHORIZATION")
        assert token, {'message': '在请求的headers中没有发现AUTHORIZATION', 'status': 401}
        try:
            jwt.decode(token, AUTH_SECRET, algorithms=['HS256'])
        except:
            raise Exception({'message': '客户端提供的TOKEN不合法', 'status': 401})
        return func(request, *args, **kwargs)

    return wrapper


def try_except(func):
    def wrapper(request, *args, **kwargs):
        result, status = {}, None
        try:
            result = func(request, *args, **kwargs)
        except (AssertionError, ValueError, Exception) as e:
            for msg in e.args:
                status = msg.get('status', 500) if isinstance(msg, dict) else 500
                message = msg.get('message') if isinstance(msg, dict) else msg
                result.update({'status': status, 'message': message})
            result['success'] = False
        else:
            pass
        finally:
            if status:
                return Response(result, status=status)
            else:
                return Response(result)

    return wrapper


def encode_token(payload):
    token = jwt.encode(payload, AUTH_SECRET, algorithm='HS256')
    return token


def decode_token(request):
    token = request.META.get("HTTP_AUTHORIZATION")
    user_data = jwt.decode(token, AUTH_SECRET, algorithms=['HS256'])
    return user_data


def model_to_dict_plus(instance, fields=None, exclude=None, timezone=None, is_meta=False):
    '''
    根据django的odel_to_dict进行扩展，添加了显示名称的写法。如某字段field为外键引用则用d_field即可获取到显示名称
    :param instance: 单个model对象，
    :param fields: 要获取的字段名称，如果没有传入则获取所有字段
    :param exclude: 要排除的字段
    :return: 整理之后的字典
    '''
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
        if not getattr(f, 'editable', False):
            continue
        if fields and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue
        f_val = getattr(instance, f.name)
        if is_meta:
            data[f.name] = f_val
            continue
        if isinstance(f_val, models.Model):
            name = getattr(f_val, 'name', None)
            full_name = getattr(f_val, 'full_name', None)
            username = getattr(f_val, 'username', None)
            data['d_{}'.format(f.name)] = name or full_name or username
            data[f.name] = f_val.id
        elif isinstance(f_val, datetime):
            data[f.name] = f_val.astimezone(timezone).isoformat() if timezone else f_val.isoformat()
        elif getattr(f, 'choices', ()):
            data['d_{}'.format(f.name)] = dict(getattr(f, 'choices', ())).get(f_val)
            data[f.name] = f_val
        else:
            data[f.name] = f_val
    return data


def get_meta_data(request):
    '''
    从headers中获取用户名，时区等信息
    :param request:
    :return:{'user': <User: root>, 'timezone': <DstTzInfo 'Asia/Shanghai' LMT+8:06:00 STD>}
    '''
    data = {}
    token = request.META.get("HTTP_AUTHORIZATION")
    user_dict = jwt.decode(token, AUTH_SECRET, algorithms=['HS256'])
    try:
        data['user'] = User.objects.get(id=user_dict.get("id"))
    except User.DoesNotExist as e:
        raise Exception({'message': 'User matching query does not exist.', 'status': 403})
    time_zone = request.META.get('TZ') or request.META.get('HTTP_TIME_ZONE') or 'Asia/Shanghai'
    data['timezone'] = timezone(time_zone)
    return data

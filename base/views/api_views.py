#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/8 23:13
# @Author  : 方新运
# @User    : fangxinyun
# @File    : api_views.py
# @Software: PyCharm
# @Describe: api

# import jwt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from utils import authorization
from utils import try_except
from base.views.select_view import select_project_view
from base.views.select_view import select_user_view
from base.views.auth_user import login_view
from base.views.group_views import UserGroupListViews
from base.views.group_views import UserGroupDetailsViews


@api_view(['GET'])
def select_projects(request, *args, **kwargs):
    result = select_project_view(request)
    return Response(result)


@api_view(['GET'])
def select_users(request, *args, **kwargs):
    result = select_user_view(request)
    return Response(result)


@api_view(['POST'])
def login(request):
    result = login_view(request)
    return Response(result)


@api_view(['GET', 'POST'])
@try_except
@authorization
def group_list(request, *args, **kwargs):
    result = UserGroupListViews(request).run(request, *args, **kwargs)
    return result


@api_view(['GET', 'DELETE', 'PATCH'])
@try_except
@authorization
def group_details(request, *args, **kwargs):
    result = UserGroupDetailsViews(request).run(request, *args, **kwargs)
    return result

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from project.models.project import Project
from base.models.user import User


def select_project_view(request):
    '''
    项目名称的下拉框
    :param params: 搜索字段
    :return: 下拉结果
    '''
    search_str = request.query_params.get('query', '')
    projects = Project.objects.filter(name__icontains=search_str).values('id', 'name')
    project_list = []
    for project in projects:
        item = {
            "value": project.get("id"),
            "label": project.get("name")
        }
        project_list.append(item)
    return project_list


def select_user_view(request):
    '''
    下拉框获取用户信息
    :param request:
    :return: 用户列表
    '''
    # token = request.META.get("HTTP_AUTHORIZATION")
    user_list = []
    users = User.objects.all()
    for user in users:
        item = {
            'value': user.id,
            'label': user.full_name or user.username
        }
        user_list.append(item)

    return user_list

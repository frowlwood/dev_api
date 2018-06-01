#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/04/08 23:13
# @Author  : 方新运
# @User    : fangxinyun
# @File    : api_views.py
# @Software: PyCharm
# @Describe: api

from rest_framework.decorators import api_view
from utils import authorization
from utils import try_except
from task.views.task_view import TaskListViews
from task.views.task_view import TaskDetailsViews
from task.views.task_view import approvalListViews
from task.views.task_view import approvalDetailsViews


@api_view(['GET', 'POST'])
@try_except
@authorization
def my_task_list(request, *args, **kwargs):
    '''
    获取任务列表，或者创建任务，其中get请求用于获取任务列表，post请求用于创建任务。
    :param request: 原始请求头
    :param args: 无可变参数
    :param kwargs:
    :return:返回任务列表或者创建成功
    '''
    result = TaskListViews(request).run(request, *args, **kwargs)
    return result


@api_view(['GET', 'DELETE', 'PUT', 'PATCH'])
@try_except
@authorization
def my_task_details(request, *args, **kwargs):
    '''
    作用包括获取任务详情，修改任务等
    :param request:
    :param args:
    :param kwargs:
    :return:
    '''
    result = TaskDetailsViews(request).run(request, *args, **kwargs)
    return result


@api_view(['GET'])
@try_except
@authorization
def approval_task_list(request, *args, **kwargs):
    result = approvalListViews(request).run(request, *args, **kwargs)
    return result


@api_view(['GET', 'PATCH'])
@try_except
@authorization
def approval_task_details(request, *args, **kwargs):
    result = approvalDetailsViews(request).run(request, *args, **kwargs)
    return result

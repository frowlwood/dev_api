#!usr/bin/env python  
# -*- coding:utf-8 _*-
# @author:fang
# @file: group_views.py
# @time: 2018/4/28/10:07
# @Software: PyCharm
# @Describe:
from base_views.base import ResourcesListViews
from base_views.base import ResourcesDetailsViews
from base.models.user_group import UserGroup


class UserGroupListViews(ResourcesListViews):
    model = UserGroup

    def __init__(self, request):
        super().__init__(request)
        self.sortable = ['name', '-write_date', '-create_date']
        self.searchable_fields = ['name']


class UserGroupDetailsViews(ResourcesDetailsViews):
    model = UserGroup
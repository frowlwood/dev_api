#!usr/bin/env python  
# -*- coding:utf-8 _*-
# @author:fang
# @file: user_group_permission.py
# @time: 2018/4/27/17:04
# @Software: PyCharm
# @Describe:

from django.db import models
from django.utils import timezone

FK_DEFAULT = {
    'null': True,
    'related_name': '+',
    'on_delete': models.CASCADE
}


class UserGroupPermission(models.Model):
    group = models.ForeignKey(u'base.Group', verbose_name=u'用户组', **FK_DEFAULT)
    permission = models.ForeignKey(u'base.Permission', verbose_name=u'权限', **FK_DEFAULT)

    create_user = models.ForeignKey(u'base.User', verbose_name=u'创建人', **FK_DEFAULT)
    create_date = models.DateTimeField(u'创建时间', null=True, default=timezone.now)
    write_user = models.ForeignKey(u'base.User', verbose_name=u'更新人', **FK_DEFAULT)
    write_date = models.DateTimeField(u'更新时间', auto_now=True)

    def __str__(self):
        return self.group

    class Meta:
        db_table = u'user_group_permission'
        verbose_name = u'用户组'

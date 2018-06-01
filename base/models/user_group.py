#!usr/bin/env python  
# -*- coding:utf-8 _*-
# @author:fang
# @file: user_group.py
# @time: 2018/4/27/11:45
# @Software: PyCharm
# @Describe:


from django.db import models
from django.utils import timezone

FK_DEFAULT = {
    'null': True,
    'related_name': '+',
    'on_delete': models.CASCADE
}

class UserGroup(models.Model):
    name = models.CharField(u'组名', max_length=64, unique=True)
    note = models.CharField(u'备注', max_length=20, null=True)

    create_user = models.ForeignKey(u'base.User', verbose_name=u'创建人', **FK_DEFAULT)
    create_date = models.DateTimeField(u'创建时间', null=True, default=timezone.now)
    write_user = models.ForeignKey(u'base.User', verbose_name=u'更新人', **FK_DEFAULT)
    write_date = models.DateTimeField(u'更新时间', auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = u'user_group'
        verbose_name = u'用户组'

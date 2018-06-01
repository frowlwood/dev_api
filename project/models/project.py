# -*- coding: utf-8 -*-
# @Time    : 2018/1/21 19:10

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


# Create your models here.
@python_2_unicode_compatible
class Project(models.Model):
    name = models.CharField(u'项目名称', max_length=256)
    desc = models.TextField(u'项目描述', null=True)

    create_user = models.ForeignKey('base.User', null=True, related_name='+', on_delete=models.CASCADE)
    create_date = models.DateTimeField(u'创建时间', null=True, auto_now_add=True)
    write_user = models.ForeignKey('base.User', null=True, related_name='+', on_delete=models.CASCADE)
    write_date = models.DateTimeField(u'更新时间', null=True, auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'project'
        verbose_name = u'项目名称'
        verbose_name_plural = u'保存了项目的基本信息'

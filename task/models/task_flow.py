#!usr/bin/env python  
# -*- coding:utf-8 _*-
# @author:fang
# @file: task_flow.py
# @time: 2018/4/10/13:46
# @Software: PyCharm
# @Describe: 任务流水表，记录所有的任务流水


from django.db import models
from django.utils import timezone


# Create your models here.
class TaskFlow(models.Model):
    TASK_STATUS = ((0, '打开'), (1, '处理中'), (2, '待审批'), (3, '回退待处理'), (4, '处理中'), (5, '已解决'), (6, '已关闭'))
    FLOW_STATUS = (('created', '已创建'), ('closed', '已关闭'), ('transferred', '已转派'))
    task = models.ForeignKey('task.Task', null=True, related_name='+', on_delete=models.CASCADE)
    user = models.ForeignKey('base.User', null=True, related_name='+', on_delete=models.CASCADE)
    task_status = models.DecimalField('任务状态', choices=TASK_STATUS, max_digits=2, decimal_places=0, default=0)
    operating = models.CharField(u'操作名称', max_length=256, null=True)
    flow_status = models.CharField('流水状态', null=True, max_length=15, choices=FLOW_STATUS, default='created')
    desc = models.TextField(u'流水描述', null=True)
    create_user = models.ForeignKey('base.User', null=True, related_name='+', on_delete=models.CASCADE)
    create_date = models.DateTimeField('创建时间', default=timezone.now)
    write_user = models.ForeignKey('base.User', null=True, related_name='+', on_delete=models.CASCADE)
    write_date = models.DateTimeField('更新时间', auto_now=True, editable=True)

    def __str__(self):
        return self.task

    class Meta:
        db_table = 'task_flow'
        verbose_name = u'任务流水表'
        verbose_name_plural = u'保存了所有的任务流水'

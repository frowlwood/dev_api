# -*- coding: utf-8 -*-
# @Time    : 2018/1/21 19:10

from django.db import models
from django.utils import timezone


# Create your models here.
class Task(models.Model):
    TASK_STATUS = (
        (0, '打开'),
        (1, '处理中'),
        (2, '待审批'),
        (3, '回退待处理'),
        (4, '处理中'),
        (5, '已解决'),
        (6, '已关闭'),
    )

    TASK_PRIORITY = (
        (3, '高'),
        (2, '中'),
        (1, '低'),
    )

    TASK_TYPE = (
        ('new', '新需求'),
        ('bug', 'Bug'),
        ('optimization', '优化意见'),
        ('deploy', '部署实施'),
        ('support', '现场支持'),
    )
    name = models.CharField(u'任务名称', max_length=256)
    status = models.DecimalField(u'任务状态', null=True, choices=TASK_STATUS, max_digits=2, decimal_places=0, default=0)
    project = models.ForeignKey('project.Project', null=True, related_name='+', on_delete=models.CASCADE)
    executor = models.ForeignKey('base.User', null=True, related_name='+', on_delete=models.CASCADE)
    leader = models.ForeignKey('base.User', null=True, related_name='+', on_delete=models.CASCADE)
    parent = models.ForeignKey('task.Task', null=True, related_name='+', on_delete=models.CASCADE)
    start_date = models.DateTimeField(u'预计开始时间', null=True)
    end_date = models.DateTimeField(u'预计结束时间', null=True)
    run_date = models.DateTimeField(u'执行时间', null=True)
    difficulty = models.DecimalField(u'难度系数', null=True, max_digits=2, decimal_places=1, default=2.5)
    priority = models.DecimalField(u'优先级', null=True, choices=TASK_PRIORITY, max_digits=1, decimal_places=0, default=2)
    type = models.CharField(u'任务类型', null=True, choices=TASK_TYPE, max_length=32, default='new')
    desc = models.TextField(u'任务描述', null=True)

    is_public = models.BooleanField(u'是否公开', default=True)
    create_user = models.ForeignKey('base.User', null=True, related_name='+', on_delete=models.CASCADE)
    create_date = models.DateTimeField(u'创建时间', null=True, default=timezone.now)
    write_user = models.ForeignKey('base.User', null=True, related_name='+', on_delete=models.CASCADE)
    write_date = models.DateTimeField(u'更新时间', null=True, auto_now=True, editable=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'task'
        verbose_name = u'任务列表'
        verbose_name_plural = u'保存了所有的任务信息'

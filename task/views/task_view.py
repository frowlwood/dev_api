#!usr/bin/env python
# -*- coding:utf-8 _*-
# @author:fang
# @file: task_view.py
# @time: 2018/4/8/10:51
# @Software: PyCharm
# @Describe:
from task.models.task import Task
from task.models.task_flow import TaskFlow
from django.db.models import Q
from datetime import datetime
from dateutil.parser import parse
from utils import model_to_dict_plus
from django.db import transaction, IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from base_views.base import ResourcesListViews
from base_views.base import ResourcesDetailsViews

OPERATING_ACTION = {
    'created': '创建任务',
    'save': '保存任务',
    'send': '发送任务',
    'submit': '提交审核',
    'cancel': '撤销审核',
    'update': '更新任务',
    'transfer': '转派任务',
    'success': '设置完成',
    'back': '回退任务',
    'close': '关闭任务'
}


def create_task_flow(uid, task, desc, action):
    old_task = TaskFlow.objects.filter(task_id=task.id).order_by('write_date').last()
    if old_task and action != 'transfer':
        old_task.flow_status = 'closed'
        old_task.save()
    elif old_task and action == 'transfer':
        old_task.flow_status = 'transferred'
        old_task.save()
    task_flow_dict = {
        'task': task,
        'user_id': uid,
        'task_status': task.status,
        'flow_status': 'created',
        'desc': desc,
        'create_user_id': uid,
        'write_user_id': uid,
        'operating': OPERATING_ACTION.get(action, '这是个测试操作')
    }
    TaskFlow.objects.create(**task_flow_dict)


class TaskListViews(ResourcesListViews):
    model = Task

    def __init__(self, request):
        super().__init__(request)
        self.sortable = ['-priority', '-end_date', '-write_date', 'project']

    def get_view_before(self, request, *args, **kwargs):
        '''
        添加过滤条件
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        status = [0, 1, 2, 3, 4, 5]
        self.or_query = (Q(executor=self.user) | Q(leader=self.user) | Q(create_user=self.user)) & Q(status__in=status)

    def post_view(self, request, *args, **kwargs):
        post_params = request.data
        form_data = post_params.get("form_data")
        with transaction.atomic():
            task = self.model.objects.create(**form_data)
            create_task_flow(self.user.id, task, None, 'created')
            result = model_to_dict_plus(task)
            return result


class TaskDetailsViews(ResourcesDetailsViews):
    model = Task

    def put_view_before(self, request, *args, **kwargs):
        '''
        提交保存和保存并发送的业务逻辑
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        params = request.data
        action = params.get('action')
        assert action in ['save', 'send'], {'message': '不支持的请求参数，put请求action必须为"save"或者"send"', 'status': 412}
        task = params.get('form_data')

        try:
            start_date = parse(task.get('start_date'))
            end_date = parse(task.get('end_date'))
        except:
            raise Exception({'message': '时间格式不正确', 'status': 412})

        new_task_dict = {
            'id': kwargs.get('id'),
            'name': task.get('name'),
            'executor_id': task.get('executor'),
            'leader_id': task.get('leader'),
            'parent_id': task.get('parent'),
            'start_date': start_date,
            'end_date': end_date,
            'difficulty': task.get('difficulty'),
            'priority': task.get('priority'),
            'type': task.get('type'),
            'desc': task.get('desc'),
            'project_id': task.get('project'),
            'create_user_id': self.user.id,
            'write_user_id': self.user.id,
        }
        if action == 'send':
            new_task_dict.update({'status': 1, 'run_date': datetime.utcnow()})
        else:
            new_task_dict.update({'status': 0})
        self.form_data = new_task_dict

    def patch_view_before(self, request, *args, **kwargs):
        params = request.data
        action = params.get("action")

        action_msg = {'message': '不支持的请求参数，match请求action必须为"submit"或者"cancel"或者"update"', 'status': 412}
        assert action in ['submit', 'cancel', 'update', 'transfer'], action_msg

        status = self.queryset.status
        form_data = {'id': kwargs.get('id')}
        if action == 'submit':
            assert status in [1, 3], {"message": '任务状态不正确', 'status': 412}
            assert self.queryset.executor_id == self.user.id, {"message": "只能把自己的任务提交到审核", 'status': 403}
            form_data.update({'status': self.queryset.status + 1})
        elif action == 'cancel':
            assert status in [2, 4], {'message': '只有待审批状态才可以撤销审核', 'status': 412}
            assert self.queryset.executor_id == self.user.id, {'message': '只有任务执行本人才可以撤销审核', 'status': 403}
            form_data.update({'status': status - 1})
        elif action == 'update':
            assert self.queryset.leader == self.user, {'message': '只有组长才能更改预期结束时间', 'status': 403}
            try:
                end_date = parse(params.get('form_data', {}).get('end_date'))
            except:
                raise Exception({'message': '请求中时间格式不正确', 'status': 412})
            form_data.update({'end_date': end_date})
        elif action == 'transfer':
            assert self.queryset.leader == self.user, {'message': '只有组长才能更改预期结束时间', 'status': 403}
            form_data.update({'executor_id': params.get('form_data', {}).get('executor_id')})
        # 把要更改的值写入到form_data中
        self.form_data = form_data
        create_task_flow(self.user.id, self.queryset, None, action)
        result = model_to_dict_plus(self.queryset, None, None, self.timezone)
        return result


class approvalListViews(ResourcesListViews):
    model = Task

    def __init__(self, request):
        super().__init__(request)
        self.sortable = ['-priority', '-end_date', '-write_date', 'project']

    def get_view_before(self, request, *args, **kwargs):
        '''
        添加过滤条件
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        self.q_dict = {
            'leader_id': self.user.id,
            'status__in': [2, 3, 4, 5]
        }


class approvalDetailsViews(ResourcesDetailsViews):
    model = Task

    def get_view(self, request, *args, **kwargs):
        '''
        get请求用于获取资源详细信息
        :param request:
        :param args:
        :param kwargs:
        :return: 资源详细信息，对外键引用进行了处理
        '''
        self.process_get_request(request, *args, **kwargs)
        try:
            queryset = self.model.objects.get(id=self.id)
        except ObjectDoesNotExist:
            raise Exception({'message': '没有查询到ID为{}的记录'.format(self.id), 'status': 400})
        result = model_to_dict_plus(queryset, self.fields, self.exclude, self.timezone)
        flow_list = []
        flow_obj = TaskFlow.objects.filter(task=queryset).order_by('create_date').select_related('user')
        for item in flow_obj:
            flow = model_to_dict_plus(item, None, None, self.timezone)
            flow_list.append(flow)
        return {'task': result, 'flow': flow_list}

    def patch_view_before(self, request, *args, **kwargs):
        params = request.data
        action = params.get('action')
        assert action in ['success', 'back', 'close'], {'message': '不支持的action参数', 'status': 412}
        note = params.get('notes')

        error_msg = {'message': '不正确的任务状态', 'status': 412}
        if action == 'success':
            assert self.queryset.status in [2, 4], error_msg
            status = 5
        elif action == 'back':
            assert self.queryset.status in [2, 4], error_msg
            status = 3
        elif action == 'close':
            assert self.queryset.status in [5], error_msg
            status = 6
        else:
            raise Exception({'message': '不支持的action参数', 'status': 412})

        with transaction.atomic():
            self.form_data = {'id': self.queryset.id, 'status': status}
            create_task_flow(self.user.id, self.queryset, note, action)
            result = model_to_dict_plus(self.queryset, None, None, self.timezone)
            return result

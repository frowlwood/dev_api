#!usr/bin/env python  
# -*- coding:utf-8 _*-
# @author:fang
# @file: base.py
# @time: 2018/4/17/15:46
# @Software: PyCharm
# @Describe:
from django.core.paginator import Paginator
from django.db.models.query_utils import Q
from utils import model_to_dict_plus
from utils import get_meta_data
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db import transaction


class ResourcesListViews(object):
    model = None

    def __init__(self, request):
        self.page_size = 10
        self.search_str = None
        self.searchable_fields = []
        self.ordering = '-write_date'
        self.page = 1
        self.fields = None
        self.exclude = None
        self.sortable = []  # 可以排序的字段，由子类定义
        self.q_dict = {}
        self.or_query = {}
        self.form_data = {}

        meta = get_meta_data(request)
        self.timezone = meta.get('timezone')
        self.user = meta.get('user')

    def run(self, request, *args, **kwargs):
        result = {}
        method = request.method
        if method.lower() == 'get':
            result = self.get_view(request, *args, **kwargs)
        elif method.lower() == 'post':
            result = self.post_view(request, *args, **kwargs)
        elif method.lower() == 'batch_delete':
            result = self.post_view(request, *args, **kwargs)
        return result

    def get_queryset(self):
        '''
        获取queryset对象，添加查询条件可以在这里添加
        :return: 返回queryset对象
        '''
        assert self.ordering in self.sortable, {'message': '非法的排序字段', 'status': 412}
        q_list = Q(**{})

        if self.search_str:
            for field_name in self.searchable_fields:
                search_dict = {field_name + '__icontains': self.search_str}
                q_obj = Q(**search_dict)
                if q_list:
                    q_list = q_list | q_obj
                else:
                    q_list = q_obj
        # 传入的且条件
        if self.q_dict and self.q_dict.keys():
            q_obj = Q(**self.q_dict)
            if q_list:
                q_list = q_list & q_obj
            else:
                q_list = q_obj
        # 条件或
        if self.or_query:
            if q_list:
                q_list = q_list & self.or_query
            else:
                q_list = self.or_query

        # quertset = self.model.objects.filter(q_list).select_related().order_by(self.ordering)
        quertset = self.model.objects.filter(q_list).select_related().order_by(self.ordering)
        return quertset

    def process_request(self, request, *args, **kwargs):
        '''
        整理get请求
        :param request:默认
        :param args: 无
        :param kwargs: 无
        :return: 没有返回值
        '''
        params = request.query_params
        if params.get('search_str'):
            self.search_str = params.get('search_str')
        if params.get('page'):
            self.page = params.get('page')
        if params.get('page_size'):
            self.page_size = params.get('page_size')
        if params.get('exclude'):
            self.exclude = params.get('exclude')
        if params.get('ordering'):
            self.ordering = params.get('ordering')
        # if params.get('searchable_fields'):
        #     self.searchable_fields = params.get('searchable_fields')
        if params.get('fields'):
            self.fields = params.get('fields')

    def get_view(self, request, *args, **kwargs):
        '''
        获取单表的数据
        :param request:默认
        :param args: 无
        :param kwargs: 无
        :return:{'count':数据数量,'data':[{数据详细信息},{},{}...]}
        '''
        self.process_request(request, *args, **kwargs)
        self.get_view_before(request, *args, **kwargs)
        contact_list = self.get_queryset()
        paginator = Paginator(contact_list, self.page_size)
        contacts = paginator.get_page(self.page)
        data = []
        for item in contacts.object_list:
            item_dict = model_to_dict_plus(item, self.fields, self.exclude, self.timezone)
            data.append(item_dict)
        result = {
            'data': data,
            'count': contacts.paginator.count
        }
        return result

    def post_view(self, request, *args, **kwargs):
        '''
        post方法，默认创建资源
        :param request:
        :param args:
        :param kwargs:
        :return: 返回创建后的资源对象
        '''
        post_params = request.data
        form_data = post_params.get("form_data")
        if not isinstance(form_data, dict):
            raise Exception({'message': '该post请求参数必须包含form_data而且值必须为json对象！', 'status': 412})
        form_data['create_user_id'] = self.user.id
        form_data['write_user_id'] = self.user.id
        with transaction.atomic():
            task = self.model.objects.create(**form_data)
            result = model_to_dict_plus(task)
            return result

    def batch_delete(self, request, *args, **kwargs):
        raise Exception({'message': '服务端没有实现针对多个资源的删除操作', 'status': 405})

    def get_view_before(self, request, *args, **kwargs):
        '''
        获取数据列表之前的方法，通过继承这个方法来过滤我们需要的数据
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        pass


class ResourcesDetailsViews(object):
    model = None

    def __init__(self, request):
        meta = get_meta_data(request)
        self.timezone = meta.get('timezone')
        self.user = meta.get('user')

        self.id = None
        self.fields = None
        self.exclude = None

        self.form_data = {}

        self.queryset = None

    def run(self, request, *args, **kwargs):
        '''
        类方法入口，用来判断请求的类型，通过不同请求来调用不通的方法
        :param request:
        :param args:
        :param kwargs:
        :return: 返回个个请求处理过后的返回值
        '''
        result = {}
        method = request.method
        if method.lower() == 'get':
            result = self.get_view(request, *args, **kwargs)
        elif method.lower() == 'post':
            result = self.post_view(request, *args, **kwargs)
        elif method.lower() == 'put':
            result = self.put_view(request, *args, **kwargs)
        elif method.lower() == 'patch':
            result = self.patch_view(request, *args, **kwargs)
        elif method.lower() == 'delete':
            result = self.delete_view(request, *args, **kwargs)
        return result

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
            self.queryset = self.model.objects.get(id=self.id)
        except ObjectDoesNotExist:
            raise Exception({'message': '没有查询到ID为{}的记录'.format(self.id), 'status': 400})
        result = model_to_dict_plus(self.queryset, self.fields, self.exclude, self.timezone)
        return result

    def post_view(self, request, *args, **kwargs):
        raise Exception({'message': '服务端没有实现针对单个资源的post请求', 'status': 405})

    def put_view(self, request, *args, **kwargs):
        '''
        PUT请求用具更新所有字段
        :param request:
        :param args:
        :param kwargs:
        :return:更新后的字段
        '''

        self.process_update_request(request, *args, **kwargs)
        with transaction.atomic():
            self.put_view_before(request, *args, **kwargs)
            assert self.form_data.get('id') == self.id and self.id, {'message': '传入参数不正确！', 'status': 412}
            try:
                new_obj = self.model(**self.form_data)
                new_obj.save()
            except ValueError as e:
                raise Exception({'message': '保存资源出错', 'status': 500})

            result = model_to_dict_plus(new_obj)
            return result

    def patch_view(self, request, *args, **kwargs):
        '''
        patch请求用与更新部分字段
        :param request:
        :param args:
        :param kwargs:
        :return: 更新后的字段
        '''
        self.process_update_request(request, *args, **kwargs)
        with transaction.atomic():
            self.patch_view_before(request, *args, **kwargs)
            assert self.form_data.get('id') == self.id and self.id, {'message': '传入参数不正确！', 'status': 412}
            query_dict = model_to_dict_plus(self.queryset, None, None, None, True)
            query_dict.update(self.form_data)
            try:
                new_obj = self.model(**query_dict)
                new_obj.save()
            except ValueError as e:
                raise Exception({'message': '保存资源出错', 'status': 500})
            except IntegrityError as e:
                error = e.args[0] if e.args else ''
                raise Exception({'message': '违反唯一性约束,原始错误信息为:{}'.format(error), 'status': 409})
            result = model_to_dict_plus(new_obj)
            return result

    def delete_view(self, request, *args, **kwargs):
        '''
        删除资源的api
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        id = kwargs.get('id')
        obj = self.model.objects.filter(id=id)
        if not obj:
            raise Exception({'message': '要删除的资源不存在', 'status': 404})
        try:
            obj.delete()
        except:
            raise Exception({'message': '删除资源出错', 'status': 400})
        obj.delete()
        return {'message': '删除id为{}的资源成功'.format(id), 'success': True, 'status': 200}

    def process_get_request(self, request, *args, **kwargs):
        '''
        get请求前对请求对象进行处理
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        params = request.query_params
        if not self.id:
            self.id = kwargs.get('id')
        assert isinstance(self.id, int) and self.id > 0, {'message': 'id必须为正整数', 'status': 412}
        self.fields = params.get('fields', [])
        self.exclude = params.get('exclude', [])

    def process_update_request(self, request, *args, **kwargs):
        '''
        在put请求patch请求中对资源进行验证，并且把获取带的queryset对象写到self里
        :param request:django请求的对象
        :param args:默认
        :param kwargs:可变参数
        :return:无返回值，但是把获取到的资源写入到self.queryset中
        '''

        if not self.id:
            self.id = kwargs.get('id')
        assert isinstance(self.id, int) and self.id > 0, {'message': 'id不正确，id应该为正整数', 'status': 412}
        if not self.queryset:
            try:
                self.queryset = self.model.objects.get(id=self.id)
            except self.model.DoesNotExist:
                raise Exception({'message': '没有查询到ID为{}的记录'.format(self.id), 'status': 400})

    def patch_view_before(self, request, *args, **kwargs):
        '''
        该方法是在path_view的基本验证通过之后，写入数据操作之前。在子类中可以通过重写该方法来实现业务级别的验证和数据的整理，
        并且在该方法执行之后应该保证 self.form_data 为需要更新的字段
        :param request:
        :param args:
        :param kwargs:
        :return: 不接受返回值
        '''

        self._add_form_data(request, *args, **kwargs)

    def put_view_before(self, request, *args, **kwargs):
        '''
        该方法执行时机为put请求通过基本验证之后，写入数据之前，在该方法执行之前资源已经在 self.queryset 中存在，
        可直接从 self.queryset 中获取数据库已经存在的数据。子类通过重写该方法，来实现对自身业务了验证和数据的整理，
        在该方法执行之后需要保证 self.form_data 为需要修改的全部数据，其中一定要包含id。
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        self._add_form_data(request, *args, **kwargs)

    def _add_form_data(self, request, *args, **kwargs):
        if not self.form_data:
            form_data = request.data.get("form_data")
            assert isinstance(form_data, dict), {'message': 'patch请求参数必须为json对象!', 'status': 412}
            form_data.setdefault('id', kwargs.get('id'))
            form_data.update({'write_user_id': self.user.id})
            self.form_data = form_data

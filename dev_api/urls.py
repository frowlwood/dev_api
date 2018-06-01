"""dev_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from base.views import api_views as base_api_views
from task.views import api_views as task_api_views

urlpatterns = [
    # path(r'base', include('base.urls')),
    path(r'base/select/projects', base_api_views.select_projects),
    path(r'base/select/users', base_api_views.select_users),
    path(r'base/login', base_api_views.login),
    path(r'base/group', base_api_views.group_list),
    path(r'base/group/<int:id>', base_api_views.group_details),

    # path(r'task', include('task.urls')),
    path(r'task/my', task_api_views.my_task_list),
    path(r'task/my/<int:id>', task_api_views.my_task_details),

    path(r'task/approval', task_api_views.approval_task_list),
    path(r'task/approval/<int:id>', task_api_views.approval_task_details),

]

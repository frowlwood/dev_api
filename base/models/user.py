# !/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone

@python_2_unicode_compatible
class UserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError('Users must have an username')

        user = self.model(
            username=username,
        )

        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None):
        user = self.model(
            username=username
        )
        user.is_admin = True
        print(password)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def __str__(self):
        return self.email


SEX_CHOICES = (("man", u"男"), ("woman", u"女"), ("unknown", u"未知"))


class User(AbstractBaseUser):
    username = models.CharField(u'登录名', max_length=20, unique=True)
    full_name = models.CharField(u'显示名称', max_length=20, null=True)
    sex = models.CharField(u'性别', choices=SEX_CHOICES, max_length=20, default="unknown")
    password = models.CharField(u'登录密码', max_length=255, null=True)
    telephone = models.CharField(u'手机号', max_length=11, null=True)
    email = models.EmailField(verbose_name=u'邮件地址', max_length=255, null=True)
    create_user = models.ForeignKey(u'base.User', null=True, related_name='+', verbose_name=u'创建人',on_delete=models.CASCADE)
    create_date = models.DateTimeField(u'创建时间', default=timezone.now)
    write_user = models.ForeignKey(u'base.User', null=True, related_name='+', verbose_name=u'更新人',on_delete=models.CASCADE)
    write_date = models.DateTimeField(u'更新时间', auto_now=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = u'username'

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    def __str__(self):
        return self.username

    class Meta:
        db_table = u'user'
        verbose_name = u'用户'

# -*- coding: utf-8 -*-
from django.db import models
from saleor.userprofile import models as saleor_models
from common import BaseModel


class UserManager(saleor_models.UserManager):

    def create_user(self, email, password=None, is_staff=False,
                    is_active=True, name=None, last_name=None, **extra_fields):
        'Creates a User with the given username, email and password'
        email = UserManager.normalize_email(email)
        user = self.model(email=email, is_active=is_active,
                          is_staff=is_staff, name=name, last_name=last_name, **extra_fields)
        if password:
            user.set_password(password)
        user.save()
        return user


class User(BaseModel, saleor_models.User):

    name = models.CharField('nombre', max_length=20)
    last_name = models.CharField('apellidos', max_length=50)
    objects = UserManager()

    def get_full_name(self):
        full_name = self.name + ' ' + self.last_name
        return full_name

    def get_short_name(self):
        return self.name

    class Meta(BaseModel.Meta):
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

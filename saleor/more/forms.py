# -*- coding: utf-8 -*-
from django import forms
from models import Product
from mptt.forms import TreeNodeChoiceField, TreeNodeMultipleChoiceField
from saleor.product.models import Category, ProductImage
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.utils.translation import ugettext_lazy as _
from saleor.more.models.user import User

class ProductForm(forms.ModelForm):

    """ Form for Product """
    categories = TreeNodeMultipleChoiceField(queryset=Category.objects.all(), label=_('Category'))

    class Meta:
        model = Product
        exclude=('available_on',)


class LoginForm(AuthenticationForm):
    """ Form para el login de usuarios registrados"""
    username = forms.EmailField(max_length=200, label='Email')

    def __init__(self, request=None, *args, **kwargs):
        super(LoginForm, self).__init__(request=request, *args, **kwargs)
        if request:
            email = request.GET.get('email')
            if email:
                self.fields['username'].initial = email


class RegisterForm(forms.Form):

    name = forms.CharField(max_length=200, label='Nombre')
    last_name = forms.CharField(max_length=200, label='Apellido')
    email = forms.EmailField(max_length=200, label='Email')
    repeat_email = forms.EmailField(max_length=200, label='Verificar Email')
    password = forms.CharField(max_length=200, label='Contraseña', widget=forms.PasswordInput())
    repeat_password = forms.CharField(max_length=200, label='Repetir Contraseña', widget=forms.PasswordInput())

    def clean(self): #llamado por is_valid
        cleaned_data = super(RegisterForm, self).clean()
        #print cleaned_data
        if len(self.errors):
            # no se puede continuar
            return cleaned_data

        if cleaned_data['password'] != cleaned_data['repeat_password']:
            raise forms.ValidationError('La contraseña no coincide', code='invalid_password_verification')
        email = cleaned_data['email']
        verify_email = cleaned_data['repeat_email']
        if email != verify_email:
            raise forms.ValidationError('El email no coincide', code='invalid_email_verification')
        
        if len(User.objects.filter(email=email)):
            #ya hay un usuario con ese email
            raise forms.ValidationError('El email ya esta siendo usado', code='invalid_email')

        return cleaned_data

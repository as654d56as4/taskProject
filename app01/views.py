from django.shortcuts import render, HttpResponse

# Create your views here.
from django import forms
from app01 import models
from django.conf import settings
from django.core.validators import RegexValidator

class RegisterModelForms(forms.ModelForm):
    phone = forms.CharField(label='手机号',validators=[RegexValidator(r'^1(3[0-9]|5[0-3,5-9]|7[1-3,5-8]|8[0-9])\d{8}$','手机号格式错误'),],widget=forms.TextInput(attrs={'class':'form-control','placeholder':'请输入手机号'}),)
    username= forms.CharField(label='用户名',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'请输入密码'}))
    password=forms.CharField(label='密码',widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'请输入密码'}))
    two_password=forms.CharField(label='重复密码',widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'请输入重复密码'}))
    email = forms.EmailField(label='邮箱',widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'请输入密码'}))
    class Meta:
        model = models.UserInfo
        fields='__all__'


def register(request):
    form=RegisterModelForms()
    return render(request,'register.html',{'form':form})
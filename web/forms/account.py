from django import forms
from web import models
from django.shortcuts import HttpResponse
from django.core.validators import RegexValidator
from django.core.validators import ValidationError
from web.forms.Bootstrap import BootStrapForm

class RegisterModelForms(BootStrapForm,forms.ModelForm):
    phone = forms.CharField(label='手机号',
                            validators=[RegexValidator(r'^1(3[0-9]|5[0-3,5-9]|7[1-3,5-8]|8[0-9])\d{8}$', '手机号格式错误'), ],
                             )
    username = forms.CharField(label='用户名',
                               )
    password = forms.CharField(label='密码', min_length=8, max_length=64,
                               error_messages={"min_length": "密码长度不能小于8", "max_length": "密码长度不能大于64"},
                               )
    two_password = forms.CharField(label='重复密码', min_length=8, max_length=64,
                                   error_messages={"min_length": "密码长度不能小于8", "max_length": "密码长度不能大于64"},
                                   )
    email = forms.EmailField(label='邮箱',)

    # clean 定义钩子函数判断数据
    def clean_username(self):  # 定义钩子函数判断用户名是否已存在
        username = self.cleaned_data['username']  # 先获取到username的值
        exists = models.UserInfo.objects.filter(username=username).exists()  # 判断值是否存在数据库
        if exists:  # 如果存在抛出用户名已存在，不存在返回username
            raise ValidationError('用户名已存在')
        return username  # 再返回username

    def clean_email(self):
        email = self.cleaned_data['email']
        exists = models.UserInfo.objects.filter(email=email).exists()
        if exists:
            raise ValidationError('邮箱已存在')
        return email

    def clean_two_password(self):
        pwd = self.cleaned_data['password']
        two_pwd = self.cleaned_data['two_password']
        if pwd != two_pwd:
            raise ValidationError('密码输出不一致')
        return two_pwd

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        exists = models.UserInfo.objects.filter(phone=phone).exists()
        if exists:
            raise ValidationError('手机号已存在')
        return phone

    class Meta:
        model = models.UserInfo
        fields = '__all__'

class loginModelForms(BootStrapForm,forms.ModelForm):
    username = forms.CharField(label='邮箱或手机号',
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入邮箱或手机号'}))

    password = forms.CharField(label='密码', min_length=8, max_length=64,
                               error_messages={"min_length": "密码长度不能小于8", "max_length": "密码长度不能大于64"},)
    code = forms.CharField(label='图片验证码',)
    def __init__(self,request,*args,**kwargs):
        # 重写init方法 增加request
        super().__init__(*args,**kwargs)
        self.request =request
    def clean_code(self):  # 钩子函数中没有request，重写一下init方法增加request
        # 读取用户输入的验证码
        code = self.cleaned_data['code']
        # 去session中获取自己的验证码
        session_code = self.request.session.get('image_code')
        if not session_code:
            raise ValidationError('验证码已过期，请重新获取')
        if code.strip().upper() != session_code.strip().upper():
            raise ValidationError('验证码错误')
        return code
    class Meta:
        model = models.loginInfo
        fields = '__all__'

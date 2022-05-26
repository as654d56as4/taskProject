from django import forms
from web import models
from web.forms.Bootstrap import BootStrapForm
from django.core.exceptions import ValidationError
from web.forms.widget import ColorRadioSelect
class ProjectModel(BootStrapForm,forms.ModelForm):
    # desc=forms.CharField(label='描述信息',widget=forms.Textarea())
    bootstrap_class_exclude = ['color']
    class Meta:
        model = models.Project
        fields=['name','color','desc']
        widgets={
            'desc':forms.Textarea,
            'color':ColorRadioSelect(attrs={'class':'color-radio'})
        }
    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.request=request

    def clean_name(self):
        '''项目校验'''
        name=self.cleaned_data['name']
        #1. 当前用户是否已创建过此项目（项目名是否已存在）？
        exists=models.Project.objects.filter(name=name,creator=self.request.tracer.user).exists()
        if exists:
            raise ValidationError('项目名已存在')
        #2. 判断当前用户还有没有额度可以创建项目？
        # 最多创建 N个项目
        #self.request.tracer.price_policy.project_num
        #当前已创建多少项目？
        count=models.Project.objects.filter(creator=self.request.tracer.user).count()
        if count>=self.request.tracer.price_policy.project_num:
            raise ValidationError('创建项目数超限，请购买套餐')
        return name
from django import forms
from web import models
from web.forms.Bootstrap import BootStrapForm


class WikiModelForm(BootStrapForm,forms.ModelForm):

    class Meta:
        model=models.Wiki
        fields=['title','content','parent']#按照规定的顺序展示这些字段
        #exclude=['project']#不展示这个字段

    def __init__(self,request,*args,**kwargs):
        # 重写init方法将父文章的值修改为自定义的值
        super().__init__(*args,**kwargs)
        #以下代码将 Model Form在数据库查出来的所有项目的数据更改为自己查询的当前项目数据
        total_data_list=[('','请选择')]
        data_list=models.Wiki.objects.filter(project=request.tracer.project).values_list('id','title') #values_list取出想要的数据
        total_data_list.extend(data_list) #extend 可以将括号内的数据赋值给自身
        self.fields['parent'].choices = total_data_list
        # 找到想要的字段 并且通过choices 重置值
        # 数据 = 去数据库中取 当前项目所有有的Wiki 标题
from django import forms
from web.forms.Bootstrap import BootStrapForm
from web import models
from django.core.exceptions import ValidationError
from utils.COS import check_file


class FileModal(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.File
        fields = ['name']

    def __init__(self, request, parent_object, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.parent_object = parent_object

    def clean_name(self):
        name = self.cleaned_data['name']
        if self.parent_object:
            exists = models.File.objects.filter(file_type=2, name=name, Project=self.request.tracer.project,
                                                parent=self.parent_object).exists()
        else:
            exists = models.File.objects.filter(file_type=2, name=name, Project=self.request.tracer.project,
                                                parent__isnull=True).exists()
        if exists:
            raise ValidationError('文件夹已存在')
        return name


class FileModalForm(forms.ModelForm):
    etag = forms.CharField(label='ETag')
    class Meta:
        model = models.File
        exclude = ['Project', 'file_type', 'update_user', 'update_datetime']  # 不需要用户传递的值  exclude 去掉
    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.request=request
    def clean_file_path(self):
        return 'https://{}'.format(self.cleaned_data['file_path'])

    def clean(self):
        key = self.cleaned_data['key']
        etag = self.cleaned_data['etag']
        size = self.cleaned_data['file_size']
        if not key or not etag:
            return self.cleaned_data

        # 向cos校验文件是否合法
        # SDK的功能
        from qcloud_cos.cos_exception import CosServiceError
        try:
            result = check_file(self.request.tracer.project.bucket,self.request.tracer.project.region,key)
        except CosServiceError as e:
            self.add_error(key,'文件不存在')
            return self.cleaned_data

        cos_etag = result.get('ETag')
        if etag != cos_etag:
            self.add_error('etag', 'ETag错误')

        cos_length = result.get('Content-Length')
        if int(cos_length) != size:
            self.add_error('size', '文件大小错误')
        return self.cleaned_data
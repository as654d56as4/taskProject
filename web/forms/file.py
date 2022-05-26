from django import forms
from web.forms.Bootstrap import BootStrapForm
from web import models
from django.core.exceptions import ValidationError


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
            exists=models.File.objects.filter(file_type=2, name=name, Project=self.request.tracer.project,
                                       parent=self.parent_object).exists()
        else:
            exists=models.File.objects.filter(file_type=2, name=name, Project=self.request.tracer.project,
                                       parent__isnull=True).exists()
        if exists:
            raise ValidationError('文件夹已存在')
        return name

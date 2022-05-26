from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms import model_to_dict
from utils.COS import Credential
from web.forms.file import FileModal
from web import models

from utils.COS import delete_file, delete_file_list


@csrf_exempt
def file(request, project_id):
    '''文件列表 & 添加文件夹'''
    parent_object = None
    folder_id = request.GET.get('folder', '')
    if folder_id.isdecimal():  # isdecimal()方法判断是不是十进制的数
        parent_object = models.File.objects.filter(id=int(folder_id), Project=request.tracer.project,
                                                   file_type=2).first()
    #  GET请求查看页面 &文件列表
    if request.method == "GET":
        breadcrumb_list = []
        parent = parent_object
        while parent:
            # breadcrumb_list.insert(0,{'id':parent.id,'name':parent.name})
            breadcrumb_list.insert(0, model_to_dict(parent, ['id', 'name']))
            parent = parent.parent
        form = FileModal(request, parent_object)
        if parent_object:
            # 进入了某个目录 有父对象
            file_object_list = models.File.objects.filter(Project=request.tracer.project,
                                                          parent=parent_object).order_by('-file_type')
        else:
            # 根目录
            file_object_list = models.File.objects.filter(Project=request.tracer.project, parent__isnull=True).order_by(
                '-file_type')
        return render(request, 'file.html', {'form': form,
                                             'file_object_list': file_object_list,
                                             'breadcrumb_list': breadcrumb_list})

    # POST请求添加文件 &修改文件夹
    fid = request.POST.get('fid', '')
    edit_object = None
    if fid.isdecimal():  # 修改
        edit_object = models.File.objects.filter(id=int(fid), Project=request.tracer.project, parent=parent_object,
                                                 file_type=2).first()
        # 添加
    if edit_object:
        form = FileModal(request, parent_object, data=request.POST, instance=edit_object)
    else:
        form = FileModal(request, parent_object, data=request.POST)
    if form.is_valid():
        form.instance.Project = request.tracer.project
        form.instance.file_type = 2
        form.instance.update_user = request.tracer.user
        form.instance.parent = parent_object
        form.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})


# http://127.0.0.1:8000/manage/32/file/delete?fid=8
def FileDelete(request, project_id):
    '''删除文件'''
    fid = request.GET.get('fid')
    # 删除数据库中的值
    delete_object = models.File.objects.filter(id=fid, Project=request.tracer.project).first()
    if delete_object.file_type == 1:
        # 删除文件 删除数据库文件、cos文件、项目已使用的空间返回

        # 将容量还给当前项目的已使用空间
        request.tracer.project.use_space -= delete_object.file_size
        request.tracer.project.save()

        # cos中删除文件
        delete_file(request.tracer.project.bucket, request.tracer.project.region, delete_object.key)

        # 在数据库中删除文件
        delete_object.delete()

        return JsonResponse({'status': True})
    # 删除文件夹 找到文件夹下所有的文件->数据库文件删除、cos文件、项目已使用的空间返回

    total_size = 0  # 已使用的文件大小
    key_list = []  # 存储在cos中要删除的文件

    folder_list = [delete_object, ]  # 目录列表
    for folder in folder_list:
        child_list = models.File.objects.filter(Project=request.tracer.project, parent=folder).order_by('-file_type')
        for child in child_list:
            if child.file_type == 2:
                folder_list.append(child)
            else:
                # 文件大小汇总
                total_size += child.file_size
                # 删除文件
                key_list.append({'Key': child.key})
    # cos批量删除
    if key_list:
        delete_file_list(request.tracer.project.bucket, request.tracer.project.region, key_list)
    # 返还容量
    if total_size:
        request.tracer.project.use_space -= total_size
        request.tracer.project.save()

    # 删除数据库中的文件
    delete_object.delete()
    return JsonResponse({'status': True})


def CosCredential(request, project_id):
    '''获取COS上传临时凭证'''
    # 他同时做容量限制： 单文件大小&总容量
    data_dict = Credential(request.tracer.project.bucket, request.tracer.project.region)
    print(data_dict)
    return JsonResponse(data_dict)

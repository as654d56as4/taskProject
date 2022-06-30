from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms import model_to_dict
from utils.COS import Credential
from web.forms.file import FileModal,FileModalForm
from web import models
import json
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
                                             'breadcrumb_list': breadcrumb_list,
                                             'folder_object': parent_object})

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


@csrf_exempt
def CosCredential(request, project_id):
    '''获取COS上传临时凭证'''

    # 获取要上传的每个文件 & 文件大小
    total_size = 0
    file_list = json.loads(request.body.decode('utf-8'))
    # 单文件容量限制
    for item in file_list:
        # 文件的字节大小 item['size'] =B
        # 超出限制 单文件限制的大小为 5M
        if item['size'] > request.tracer.price_policy.per_file_size * 1024 * 1024:  # M 转化为 B
            return JsonResponse({'status': False,
                                 'error': '单文件超出限制（最大{}M），文件：{}'.format(request.tracer.price_policy.per_file_size,
                                                                        item['size'])})
        total_size += item['size']

    # 总容量限制
    # request.tracer.price_policy.project_space  # 项目允许的空间
    # request.tracer.project.use_space  # 项目已使用空间
    if request.tracer.project.use_space + total_size > request.tracer.price_policy.project_space * 1024 * 1024 * 1024:
        return JsonResponse({'status': False, 'error': '容量超过最大限制，请购买套餐'})
    # 同时做容量限制： 单文件大小&总容量
    data_dict = Credential(request.tracer.project.bucket, request.tracer.project.region)  # 临时凭证
    return JsonResponse({'status': True, 'data': data_dict})


@csrf_exempt
def FilePost(request, project_id):
    '''已上传文件写入数据库'''
    '''
    name:fileName, 
    key:key,
    file_size:fileSize,
    parent:CURRENT_FOLDER_ID,
    # etag:data.ETag,
    file_path:data.Location,
    '''
    # 根据key再去cos获取文件Etag
    print(request.POST)
    form = FileModalForm(request,data=request.POST)
    if form.is_valid():
        # 校验通过：数据写入数据库
        # form.instance.file_type = 1
        # form.instance.update_user = request.tracer.user
        # 通过ModelForm.save存储到数据库中的数据返回的instance对象，无法通过get_xx_display获取choice的中文
        # form.save()
        data_dict= form.cleaned_data
        data_dict.pop('etag')
        data_dict.update({'Project':request.tracer.project,'file_type':1,'update_user':request.tracer.user})
        instance = models.File.objects.create(**data_dict)

        # 项目已使用空间：更新
        request.tracer.project.use_space += instance.file_size
        request.tracer.project.save()
        result= {
            'name':instance.name,
            #'file_type':instance.get_file_type_display(),
            'file_size':instance.file_size,
            'update_user':instance.update_user.username,
            'update_datetime':instance.update_datetime,
        }
        return JsonResponse({'status':True,'data':result})

    return JsonResponse({'status':False,'data':'文件错误'})

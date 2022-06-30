from django.shortcuts import render, redirect
from web.forms.project import ProjectModel
from django.http import JsonResponse
from web import models
from utils.COS import create_bucket
import time


def project_list(request):
    if request.method == 'GET':
        # get请求查看项目列表
        '''
        1.丛数据库中获取两部分数据
            我创建的项目：已星标、未星标
            我参与的项目：已星标、未星标
        2.提取已星标
            列表 = 循环[我创建的项目]+[我参与的项目] 把已星标的数据提取
        
        得到三个列表：星标、创建、参与
        '''
        project_dict = {'star': [], 'my': [], 'join': []}
        my_project_list = models.Project.objects.filter(creator=request.tracer.user)
        for row in my_project_list:
            if row.star:
                project_dict['star'].append({'value': row, 'type': 'my'})
            else:
                project_dict['my'].append(row)
        join_project_list = models.ProjectUser.objects.filter(user=request.tracer.user)
        for item in join_project_list:
            if item.star:
                project_dict['star'].append({'value': item.project, 'type': 'join'})
            else:
                project_dict['join'].append(item.project)
        form = ProjectModel(request)
        return render(request, 'project_list.html', {'form': form, 'project_dict': project_dict})

    form = ProjectModel(request, data=request.POST)
    if form.is_valid():
        # 1.创建项目之前为项目创建一个桶
        "桶名：{手机号}-{时间戳}-1309173579"
        bucket = "{}-{}-1309173579".format(request.tracer.user.phone, str(int(time.time() * 1000)))
        region = 'ap-nanjing'
        create_bucket(bucket, region)
        # 2.桶和区域也要写入数据库
        form.instance.region = region
        form.instance.bucket = bucket
        # 验证通过：项目名、颜色、描述+Creator
        form.instance.creator = request.tracer.user
        # 3.创建项目
        form.save()
        return JsonResponse({'status': True, 'data': 'list'})
    return JsonResponse({'status': False, 'error': form.errors})


def project_star(request, project_type, project_id):
    '''星标项目'''
    if project_type == 'my':
        # 改为星标项目只需要找到这个项目然后使用update修改star的值为True就可以；
        models.Project.objects.filter(creator=request.tracer.user, id=project_id).update(star=True)
        return redirect('project_list')
    if project_type == 'join':
        models.ProjectUser.objects.filter(project_id=project_id, user=request.tracer.user).update(star=True)
    return redirect('project_list')


def project_unstar(request, project_type, project_id):
    '''取消星标'''
    if project_type == 'my':
        # 改为星标项目只需要找到这个项目然后使用update修改star的值为True就可以；
        models.Project.objects.filter(creator=request.tracer.user, id=project_id).update(star=False)
        return redirect('project_list')
    if project_type == 'join':
        models.ProjectUser.objects.filter(project_id=project_id, user=request.tracer.user).update(star=False)
    return redirect('project_list')

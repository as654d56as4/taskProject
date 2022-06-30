from django.shortcuts import render, HttpResponse, redirect
from web.forms.Wiki import WikiModelForm
from web.models import Wiki
from web import models
from django.http import JsonResponse
from django.forms import forms
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from utils.uid import uid
from utils.COS import upload_file


def wiki(request, project_id):
    """Wiki首页"""
    wiki_id = request.GET.get('wiki_id')  # 拿到当前项目的id并通过id和当前项目找到wiki对象
    wiki_object = models.Wiki.objects.filter(id=wiki_id, project=request.tracer.project).first()
    return render(request, 'wiki.html', {'wiki_object': wiki_object})


def demo(request, project_id):
    """Wiki添加文章"""
    if request.method == 'GET':
        form = WikiModelForm(request)
        return render(request, 'demo.html', {'form': form})
    form = WikiModelForm(request, data=request.POST)
    if form.is_valid():
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.depth = 1
        form.instance.project = request.tracer.project
        form.save()
        url = reverse('wiki', kwargs={'project_id': project_id})  # 反向生成url
        return redirect(url)


def catalog(request, project_id):
    """wiki目录"""
    # 获取当前项目所有的目录
    # data=models.Wiki.objects.filter(project=request.tracer.project).values('id','title','parent_id')
    data = models.Wiki.objects.filter(project=request.tracer.project).values('id', 'title', 'parent_id').order_by(
        'depth', 'id')
    return JsonResponse({'status': True, 'data': list(data)})


def delete(request, project_id, wiki_id):
    '''删除文章'''
    models.Wiki.objects.filter(project_id=project_id, id=wiki_id).delete()
    url = reverse('wiki', kwargs={'project_id': project_id})
    return redirect(url)


def edit(request, project_id, wiki_id):
    wiki_object = models.Wiki.objects.filter(project_id=project_id, id=wiki_id).first()
    if not wiki_object:
        url = reverse('wiki', kwargs={'project_id': project_id})
        return redirect(url)
    if request.method == 'GET':
        form = WikiModelForm(request, instance=wiki_object)  # instance 表示从数据库中取值，data表示用户传递的值
        return render(request, 'demo.html', {'form': form})
    form = WikiModelForm(request, data=request.POST, instance=wiki_object)  # instance 表示从数据库中取值，data表示用户传递的值
    if form.is_valid():
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.depth = 1
        form.instance.project = request.tracer.project
        form.save()
        url = reverse('wiki', kwargs={'project_id': project_id})  # 反向生成url
        preview_url = "{0}?wiki_id={1}".format(url, wiki_id)  # 字符串格式化
        return redirect(preview_url)
    return render(request, 'demo.html', {'form': form})


@csrf_exempt  # 这个视图函数免除csrf 的认证
def upload(request, project_id):
    '''markdown插件上传图片'''
    print('收到图片')
    result = {
        'success': 0,
        'message': None,
        'url': None,
    }
    img_object = request.FILES.get('editormd-image-file')  # 拿到img对象
    if not img_object:
        result['message'] = '文件不存在'
        return JsonResponse(result)
    ext = img_object.name.rsplit('.')[-1]  # 拿到文件后缀名
    key = '{}.{}'.format(uid(request.tracer.user.phone), ext)  # COS桶中文件的名称 uid自定义函数
    # 文件对象上传到当前项目的桶中
    img_url = upload_file(
        request.tracer.project.bucket,
        request.tracer.project.region,
        img_object,
        key
    )
    print(img_url)
    result['success'] = 1
    result['url'] = img_url
    return JsonResponse(result)

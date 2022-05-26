from django.template import Library
from web import models
from django.urls import reverse # 在python代码中反向解析url地址需要使用的模块

register = Library()


@register.inclusion_tag('inclusion/all_project_list.html')
##基于inclusiontag展示
# 中间件是所有页面加载之前就会执行，inclusiontag在需要使用的页面导入。
def all_project_list(request):
    ##获取我创建的项目
    my_project_list = models.Project.objects.filter(creator=request.tracer.user)
    ##获取我参与的项目
    join_project_list = models.ProjectUser.objects.filter(user=request.tracer.user)
    return {'my': my_project_list, 'join': join_project_list,'request':request}


@register.inclusion_tag('inclusion/manage_list.html')
def manage_list(request):
    dict_list = [#此功能实现项目列表展示
        {'title': '概述', 'url': reverse('dashboard', kwargs={'project_id': request.tracer.project.id})},
        {'title': '问题', 'url': reverse('issues', kwargs={'project_id': request.tracer.project.id})},
        {'title': '统计', 'url': reverse('statistics', kwargs={'project_id': request.tracer.project.id})},
        {'title': 'wiki', 'url': reverse('wiki', kwargs={'project_id': request.tracer.project.id})},
        {'title': '文件', 'url': reverse('file', kwargs={'project_id': request.tracer.project.id})},
        {'title': '配置', 'url': reverse('setting', kwargs={'project_id': request.tracer.project.id})},
    ]
    for item in dict_list:##此功能实现鼠标点击选中效果 增加class
        #request.path_info可以拿到当前用户访问的url
        #去跟dict_list中每个url进行比较 看那个开头相同
        if request.path_info.startswith(item['url']):
            #判断当前访问的url 的开头和dict_list中的哪个字典相同就给这个字典赋一个值 然后在前端页面判断class存在的话就添加一个active属性
            item['class']='active'
    return {'dict_list':dict_list}

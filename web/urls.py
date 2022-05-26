"""a1project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from web.views import account, home, project, manage, Wiki, file

urlpatterns = [
    # 注册、登录、退出、验证码、首页
    url(r'^register', account.register, name='register'),
    url(r'^login', account.login, name='login'),
    url(r'^img_code', account.img_code, name='img_code'),
    url(r'^index', home.index, name='index'),
    url(r'^logout', account.logout, name='logout'),

    # 项目列表
    url(r'^project/list', project.project_list, name='project_list'),

    # 添加星标/取消星标
    # 路由：project/star/my/1
    # 路由：project/star/join/1
    url(r'^project/star/(?P<project_type>\w+)/(?P<project_id>\d+)', project.project_star, name='project_star'),
    url(r'^project/unstar/(?P<project_type>\w+)/(?P<project_id>\d+)', project.project_unstar, name='project_unstar'),

    # w匹配字母，d匹配数字

    # 概述
    url(r'^manage/(?P<project_id>\d+)/dashboard', manage.dashboard, name='dashboard'),

    # 问题
    url(r'^manage/(?P<project_id>\d+)/issues', manage.issues, name='issues'),

    # 统计
    url(r'^manage/(?P<project_id>\d+)/statistics', manage.statistics, name='statistics'),

    # 文件
    url(r'^manage/(?P<project_id>\d+)/file', file.file, name='file'),
    url(r'^manage/(?P<project_id>\d+)/FileDelete', file.FileDelete, name='FileDelete'),
    url(r'^manage/(?P<project_id>\d+)/CosCredential', file.CosCredential, name='CosCredential'),

    # 文档
    url(r'^manage/(?P<project_id>\d+)/wiki', Wiki.wiki, name='wiki'),
    url(r'^manage/(?P<project_id>\d+)/catalog', Wiki.catalog, name='catalog'),
    url(r'^manage/(?P<project_id>\d+)/demo', Wiki.demo, name='demo'),
    url(r'^manage/(?P<project_id>\d+)/upload', Wiki.upload, name='upload'),
    url(r'^manage/(?P<project_id>\d+)/edit/(?P<wiki_id>\d+)', Wiki.edit, name='edit'),
    url(r'^manage/(?P<project_id>\d+)/delete/(?P<wiki_id>\d+)', Wiki.delete, name='delete'),

    # 配置
    url(r'^manage/(?P<project_id>\d+)/setting', manage.setting, name='setting'),
]

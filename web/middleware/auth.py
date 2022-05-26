from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from web import models
from django.conf import settings
import datetime

class Tracer(object):
    def __init__(self):
        self.user = None
        self.price_policy=None
        self.project=None
# 中间件 页面跳转之前会自动进行判断
class AuthMiddleware(MiddlewareMixin):
    # process_request方法 进入网站就自动执行
    def process_request(self, request):
        request.tracer = Tracer()
        # 用户登录时给request.session['user_id']赋了值
        user_id = request.session.get('user_id', 0)
        # 查询userinfo表中的值为noneor空，查询不到
        user_object = models.UserInfo.objects.filter(id=user_id).first()
        # 用户没登录就是none，查询不到， 登录就有值
        # 将数据赋值给tracer
        request.tracer.user = user_object

        # 白名单 里面写没登录也可以访问的url 添加到settigns
        '''
        1.获取到当前用户访问的url。
        2.检查url是否在白名单中，如果在则继续向后访问，如果不在，判断是否登录
        '''
        # 获取到当前用户输入的url   request.path_info
        # print(request.path_info)
        # 获取到settings中的白名单 settings.WHITE_REGEX_URL_LIST
        if request.path_info in settings.WHITE_REGEX_URL_LIST:
            return  # return 是直接返回用户的url
        if not request.tracer.user:
            return redirect('login')

        # 登录成功后，访问后台管理，获取当前用户拥有的额度
        # 获取当前用户ID值最大（最近的交易记录）
        _object = models.Transaction.objects.filter(user=user_object, status=2).order_by('-id').first()
        # 判断最近的交易记录是否已过期
        current_datetime = datetime.datetime.now()
        # 判断当前时间小于交易记录结束时间并且结束时间存在的话
        if _object.end_datetime == current_datetime:
            # 就把最近的交易记录修改为id最小的交易记录
            _object = models.Transaction.objects.filter(user=user_object, status=2,price_policy__category=1).first()
        request.tracer.price_policy=_object.price_policy
    # process_view是在路由匹配通过之后执行
    def process_view(self, request,view,args,kwargs):
        #判断路由是否以manage开头
        if not request.path_info.startswith('/manage'):
            return

        #判断project_id是否为我创建的 or 我参与的
        project_id= kwargs.get('project_id')#可以拿到当前项目的id
        #去数据库中查询当前用户输入的路由中project_id部分是否存在数据库中，如果不存在继续往下走
        project_object=models.Project.objects.filter(creator=request.tracer.user,id=project_id).first()
        if project_object:
            #是我创建的项目就让他通过
            #封装到request中方便之后访问
            request.tracer.project=project_object
            return
        #如果不是我创建的项目 在看是不是我参与的项目
        project_user_object=models.ProjectUser.objects.filter(user=request.tracer.user,project_id=project_id).first()
        if project_user_object:
            #是我参与的项目也让他通过
            # 封装到request中方便之后访问
            request.tracer.project =project_user_object.project
            return
        #如果都不是，则认为用户在捣乱，测试别人的项目，则给他返回项目列表
        return redirect('project_list')
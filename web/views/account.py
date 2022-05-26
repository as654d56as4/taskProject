from django.shortcuts import render, HttpResponse, redirect
from web.forms.account import RegisterModelForms, loginModelForms
from django.http import JsonResponse
from web import models
import uuid
import datetime
from scripts import base

def register(request):
    '注册页面'
    if request.method == 'GET':  # 判断页面请求是get
        form = RegisterModelForms()  # 实例化表单
        return render(request, 'register.html', {'form': form})  # 传递参数
    form = RegisterModelForms(data=request.POST)
    if form.is_valid():
        # 验证通过后写入数据库
        instance=form.save()  # 将数据保存到数据库
        price_policy=models.PricePolicy.objects.filter(category=1,title="个人免费版").first()
        models.Transaction.objects.create(
            status=2,
            order=str(uuid.uuid4()), #uuid.uuid4()可以生成一个随机字符串
            user=instance,
            price_policy=price_policy,
            count=0,
            price=0,
            start_datetime=datetime.datetime.now(), #获取到当前的系统时间
            end_datetime=datetime.datetime.now(),
        )
        return JsonResponse({'status': True, 'data': '/login/'})  # 验证成功返回状态为true 并返回一个跳转地址
    return JsonResponse({'status': False, 'error': form.errors})  # 验证失败返回状态为false，并返回错误信息


def login(request):
    '用户名和密码登录'
    if request.method == 'GET':
        form = loginModelForms(request)
        return render(request, 'login.html', {'form': form})
    form = loginModelForms(request, data=request.POST)
    if form.is_valid():
        # cleaned_data拿到的是用户输入的数据
        #先拿到用户输入的值
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        # user_object = models.UserInfo.objects.filter(username=username).first()
        from django.db.models import Q
        # or关系查询使用Q
        # 查询UserInfo表中的数据，成功为True
        # 用手机号或者邮箱登录
        user_object = models.UserInfo.objects.filter(Q(email=username) | Q(phone=username)).filter(
            password=password).first()
        # 判断user_object是否为True
        if user_object:
            # 登录成功给session增加user_id，把user_object.id赋值到user_id字段，中间件会用到
            request.session['user_id'] = user_object.id
            #超时时间改回两周
            request.session.set_expiry(60 * 60 * 24 * 14)
            #返回地址 index
            return redirect('index')
        #user_object为False 表示用户输入的值数据库中不存在，使用form.add_error获取到当前字段的错误信息
        form.add_error('username', '用户名或密码错误')
        #报错之后将页面重新返还给用户
        return render(request, 'login.html', {'form': form})


def img_code(request):  # https://www.cnblogs.com/wupeiqi/articles/5812291.html 图片验证码博客
    '''生成图片验证码'''
    from io import BytesIO
    from utils.image_code import check_code
    # 生成一个图片对象和验证码文字
    img_object, code = check_code()

    # 主动修改session的过期时间为60s默认过期时间为两周
    request.session.set_expiry(60)
    # 创建一个内存
    stream = BytesIO()
    # 将验证码赋值给session中的img_session做判断
    request.session['image_code'] = code
    # 将图片保存到内存中
    img_object.save(stream, 'png')
    # 直接返回图片
    return HttpResponse(stream.getvalue())

def logout(request):
    # 清除session中的值，退出登录状态
    request.session.flush()  #flush()清空session中的值
    #返回首页
    return redirect('index')
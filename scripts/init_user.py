# django离线脚本运行需要导入
# 数据库存储大量的数据使用离线脚本省时省力 需要存储大量的数据时使用离线脚本
import django
import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(base_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "a1project.settings")
# os.environ['DJANGO_SETTINGS_MODULE']读到当前项目a1project的settings
django.setup()  # 模拟启动当前settings项目
from web import models

models.UserInfo.objects.create(username='蔡家豪', email='2322791942@qq.com', phone='13170474504', password='123123')

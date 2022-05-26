import django
import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(base_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "a1project.settings")
# os.environ['DJANGO_SETTINGS_MODULE']读到当前项目a1project的settings
django.setup()  # 模拟启动当前settings项目
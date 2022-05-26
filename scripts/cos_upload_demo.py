# -*- coding=utf-8
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import logging


# 正常情况日志级别使用INFO，需要定位时可以修改为DEBUG，此时SDK会打印和服务端的通信信息
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

secret_id = 'AKIDDLVVZUDk5MeBiElM0ncSUajrEe7bBnQz'     # 替换为用户的 SecretId，请登录访问管理控制台进行查看和管理，https://console.cloud.tencent.com/cam/capi
secret_key = 'iMzbEXo6MZlHgIX1SuItT4gElEfIwcHW'   # 替换为用户的 SecretKey，请登录访问管理控制台进行查看和管理，https://console.cloud.tencent.com/cam/capi
region = 'ap-nanjing'
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
client = CosS3Client(config)
response = client.upload_file(
    Bucket='tracer-1309173579',
    LocalFilePath=r'C:\Users\MAX\Desktop\简历图.png', #本地文件的路径
    Key='p1.png', #上传到桶之后的文件名
)
print(response['ETag'])
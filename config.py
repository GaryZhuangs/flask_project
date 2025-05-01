# This file contains the configuration of the Flask application.
import os
from datetime import timedelta, datetime

BASE_DIR = os.path.dirname(__file__)
DB_USERNAME = 'root'
DB_PASSWORD = '123456'
DB_HOST = 'localhost'
DB_NAME = 'pythonbbs'
DB_PORT = '3306'
DB_URL='mysql+pymysql://{}:{}@{}:{}/{}'.format(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
SQLALCHEMY_DATABASE_URI = DB_URL
SQLALCHEMY_TRACK_MODIFICATIONS = False

# upciqzhgxsqubbci
# MAIL_USE_TLS：端口号587
# MAIL_USE_SSL：端口号465
# QQ邮箱不支持非加密方式发送邮件
# 发送者邮箱的服务器地址
MAIL_SERVER = "smtp.qq.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
# MAIL_USE_SSL = True
MAIL_USERNAME = "943580899@qq.com"
MAIL_PASSWORD = "upciqzhgxsqubbci"
MAIL_DEFAULT_SENDER = "943580899@qq.com"

# Celery的Redis配置
CELERY_BROKER_URL ='redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND ='redis://127.0.0.1:6379/0'

# FLASK-Caching
CACHE_TYPE = 'RedisCache'
CACHE_DEFAULT_TIMEOUT = 300
CACHE_REDIS_HOST = '127.0.0.1'
CACHE_REDIS_PORT = 6379
CACHE_REDIS_DB = 0

# SECRET_KEY
SECRET_KEY = 'upciqzhgxsqubbci'

# Session=turn 过期时间
PERMANENT_SESSION_LIFETIME = timedelta(days=7)

# 头像配置
AVATARS_SAVE_PATH = os.path.join(BASE_DIR, 'media','avatars')

# 图片上传配置
POST_IMAGE_SAVE_PATH = os.path.join(BASE_DIR, 'media','post')

# banner图片上传配置
BANNER_IMAGE_SAVE_PATH = os.path.join(BASE_DIR, 'media','banner')

# 每页展示帖子数量
POSTS_PER_PAGE = 10

# 设置JWT的密钥
JWT_SECRET_KEY='upciqzhgxsqubbci'
JWT_ACCESS_TOKEN_EXPIRES=timedelta(days=7)
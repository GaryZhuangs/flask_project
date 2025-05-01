# This is the main file of the Flask project.
from flask import Flask
from flask_project import config
from .exts import db,mail,cache,csrf,avatars,jwt,cors
from flask_migrate import Migrate
from .apps.front import front_bp
from .bbs_celery import make_celery
from flask_project.apps.media import media_bp
from flask_project.apps.cmsapi import cmsapi_bp
from flask_project import commands
app = Flask(__name__)
app.config.from_object(config)
# 加载配置
db.init_app(app)
# 初始化数据库
mail.init_app(app)
# 初始化邮件
cache.init_app(app)
# 初始化缓存
csrf.init_app(app)
# 初始化CSRF保护
avatars.init_app(app)
# 初始化头像
migrate = Migrate(app, db)
mycelery = make_celery(app)
# 初始化迁移, 将orm模型生成迁移脚本 ：flask db migrate -m "message", 运行迁移脚本 ：flask db upgrade
app.register_blueprint(front_bp)
app.register_blueprint(media_bp)
app.register_blueprint(cmsapi_bp)
# 注册蓝图
jwt.init_app(app)
# 初始化JWT
cors.init_app(app, resources={r"/cmsapi/*": {"origins": "*"}})
# 初始化跨域

csrf.exempt(cmsapi_bp)
#排除cmsapi的csrf保护
# 注册命令
app.cli.command("init_boards")(commands.init_boards)
app.cli.command("create_test_posts")(commands.create_test_posts)
app.cli.command("init_roles")(commands.init_roles)
app.cli.command("bing_roles")(commands.bing_roles)

#celery -A flask_project.app.mycelery worker --loglevel=info -P gevent
# 启动celery
if __name__ == '__main__':
    app.run(debug=True)
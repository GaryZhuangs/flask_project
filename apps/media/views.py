from flask import Blueprint,send_from_directory,current_app
bp = Blueprint('media', __name__,url_prefix='/media')

# /media/avatar/abc.jpg
# 部署的时候，在nginx中配置一个/media前缀的url
# 访问/media/avatar/abc.jpg的时候，会自动去找/media/avatar/abc.jpg这个文件

@bp.route('/avatar/<filename>') # 访问/media/avatar/abc.jpg ，用户头像设置
def get_avatar(filename):
    return send_from_directory(current_app.config['AVATARS_SAVE_PATH'],filename)

@bp.route('/post/<filename>') # 访问/media/post/abc.jpg ，文章图片设置
def get_post_image(filename):
    return send_from_directory(current_app.config['POST_IMAGE_SAVE_PATH'],filename)

@bp.route('/banner/<filename>') # 访问/media/comment/abc.jpg ，评论图片设置
def get_banner_image(filename):
    return send_from_directory(current_app.config['BANNER_IMAGE_SAVE_PATH'],filename)



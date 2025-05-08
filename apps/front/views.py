from datetime import datetime,timedelta
import os
from flask import (Blueprint, request, render_template,
                   jsonify, current_app, make_response,
                   redirect, session, g, url_for)
import string, random
from flask_mail import Mail, Message
from flask_project.exts import cache
from flask_project.utils import restful
from flask_project.utils.captcha import Captcha
from flask_project.apps.front.froms import (RegisterForm, LoginForm, UploadAvatarForm,
                                            EditProfileForm, UploadimageForm, PublicPostForm,
                                            PublicCommentForm,ResetPasswordForm)
from flask_project.models.auto import UserModel,Permission
from flask_project.models.post import BoardModel, PostModel, CommentModel,CollectModel
from flask_project.exts import db
import time
from hashlib import md5
from io import BytesIO
from flask_project.templates.front.decorators import login_required
from flask_avatars import Identicon
from flask_paginate import get_page_parameter, Pagination
from sqlalchemy.sql import func
from flask_jwt_extended import create_access_token
from flask_project.models.post import BannerModel

bp = Blueprint('front', __name__, url_prefix='/')


@bp.before_request
def front_before_request():  # 请求之前，先执行这个函数（检查用户是否登录，并把用户信息赋值给g.user）
    if 'user_id' in session:  # 如果session中有user_id，则从数据库中查询用户信息并赋值给g.user
        user = UserModel.query.get(session['user_id'])  # 查询用户信息
        setattr(g, 'user', user)  # 给g.user赋值


# 请求=>before_request=>视图函数（返回模板）=>context_processor=>模板渲染 =>响应

# 上下文处理器
@bp.context_processor
def front_context_processor():  # 响应之前，先执行这个函数
    if hasattr(g, 'user'):
        return {'user': g.user}
    else:
        return {}



@bp.route('/cms')
def cms():
    return render_template('cms/index.html')

@bp.route('/search')
def search():
    q = request.args.get('q')
    posts=PostModel.query.filter(PostModel.title.contains(q)).all()
    return render_template("front/base.html",posts=posts)

@bp.route('/')
def index():
    sort = request.args.get('sort', type=int, default=1)
    borad_id = request.args.get('bd', type=int, default=None)
    boards = BoardModel.query.order_by(BoardModel.priority.desc()).all()
    post_query = None
    if sort == 1:
        post_query = PostModel.query.order_by(PostModel.create_time.desc())
    elif sort == 2:
        # 根据评论数量进行排序
        post_query = db.session.query(PostModel).outerjoin(CommentModel).group_by(PostModel.id).order_by(
            func.count(CommentModel.id).desc(), PostModel.create_time.desc())
    elif sort == 3:
        # 根据收藏数量进行排序
        post_query = db.session.query(PostModel).outerjoin(CollectModel).group_by(PostModel.id).order_by(func.count(CollectModel.id).desc(), PostModel.create_time.desc())
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * current_app.config['POSTS_PER_PAGE']
    end = start + current_app.config['POSTS_PER_PAGE']

    if borad_id:
        post_query = post_query.filter(PostModel.board_id == borad_id)

    total = post_query.count()
    posts = post_query.slice(start, end)
    pagination = Pagination(bs_version=3, page=page, total=total, prev_label='上一页', next_label='下一页')
    banners=BannerModel.query.order_by(BannerModel.priority.desc()).all()
    context = {
        'boards': boards,
        'posts': posts,
        'pagination': pagination,
        'st': sort,
        'bd': borad_id,
        'banners':banners
    }
    return render_template("front/index.html", **context)


@bp.get('/email/captcha')
def email_captcha():
    email = request.args.get('email')
    if not email:
        return restful.params_error(message='邮箱不能为空')
    source = list(string.digits)
    captcha = ''.join(random.sample(source, 6))
    print(captcha)
    subject = 'IT之家注册验证码'
    body = "【IT之家】您的注册验证码为：%s" % captcha
    # 生成验证码
    current_app.celery.send_task('send_mail', (email, subject, body))
    cache.set(email, captcha, timeout=60 * 5)
    cache.get(email)
    return restful.ok(message="验证码已发送至邮箱，请查收")


@bp.route('/graph/captcha') # 生成图片验证码
def email_captcha_check():
    captcha, graph = Captcha.gene_graph_captcha()
    key = md5((captcha + str(time.time())).encode('utf-8')).hexdigest()
    cache.set(key, captcha)
    # 将验证码存入缓存
    # with open('captcha.png', 'wb')as fp:
    #    graph.save(fp ,'png')
    out = BytesIO()
    graph.save(out, 'png')
    out.seek(0)
    # 将文件指针移动到开头
    resp = make_response(out.read())
    resp.content_type = 'image/png'
    resp.set_cookie('captcha_key', key, max_age=3600)
    return resp


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("front/login.html")
    else:
        form = LoginForm(request.form)
        if form.validate():
            email = form.email.data
            password = form.password.data
            remember = form.remember.data
            user = UserModel.query.filter_by(email=email).first()
            if not user:
                return restful.params_error(message='邮箱或密码错误')
            if not user.check_password(password):
                return restful.params_error(message='邮箱或密码错误')
            if user.is_active == 0:
                return restful.params_error(message='用户已被禁用')
            session['user_id'] = user.id
            # 如果是员工才能创建token
            token = ""
            permissions = []
            if user.is_staff:
                token = create_access_token(identity=user.id)
                for attr in dir(Permission):
                    if not attr.startswith("_"):
                        permission = getattr(Permission, attr)
                        if user.has_permission(permission):
                            permissions.append(attr.lower())
            if remember == 1:
                # 默认session过期时间，就是只要浏览器关闭了就会过期
                session.permanent = True
            user_dict = user.to_dict()
            user_dict['permissions'] = permissions
            return restful.ok(data={"token": token, "user": user_dict})
        else:
            return restful.params_error(message=form.messages[0])


@bp.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("front/register.html")
    else:
        form = RegisterForm(request.form)
        if form.validate():
            email = form.email.data
            username = form.username.data
            password = form.password.data
            identicon = Identicon()
            filenames = identicon.generate(text=md5(email.encode('utf-8')).hexdigest())
            avatar = filenames[2]

            user = UserModel(email=email, username=username, password=password, avatar=avatar)
            db.session.add(user)
            db.session.commit()
            return restful.ok()
        else:
            message = form.messages[0]
            return restful.params_error(message=message)

@bp.route("/resetpwd",methods=['GET','POST'])
def resetpwd():
    if request.method == 'GET':
        return render_template("front/resetpwd.html")
    else:
        form = ResetPasswordForm(request.form)
        if form.validate():
            email = form.email.data
            password = form.password.data
            user = UserModel.query.filter_by(email=email).first()
            if not user:
                return restful.params_error(message='邮箱不存在')
            user.password = password
            db.session.commit()
            return restful.ok()
        else:
            return restful.params_error(message=form.messages[0])


@bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@bp.route('/setting')
@login_required
def setting():
    email_hash = md5(g.user.email.encode('utf-8')).hexdigest()
    return render_template("front/setting.html", email_hash=email_hash)


@bp.post("/avatar/upload")
@login_required
def upload_avatar():
    form = UploadAvatarForm(formdata=request.files)  # 修改初始化方式
    if form.validate():
        image = form.image.data
        filename = image.filename
        _, ext = os.path.splitext(filename)
        filename = md5((g.user.email + str(time.time())).encode('utf-8')).hexdigest() + ext
        image_path = os.path.join(current_app.config['AVATARS_SAVE_PATH'], filename)
        image.save(image_path)
        g.user.avatar = filename
        db.session.commit()
        return restful.ok(data={'avatar': filename})
    else:
        message = form.messages[0]
        return restful.params_error(message=message)


@bp.post("/profile/edit")
@login_required
def profile_edit():
    form = EditProfileForm(formdata=request.form)
    if form.validate():
        signature = form.signature.data
        username=form.username.data
        g.user.signature = signature
        g.user.username=username
        db.session.commit()
        return restful.ok()
    else:
        return restful.params_error(message=form.messages[0])


@bp.route("/post/public", methods=['GET', 'POST'])
@login_required
def public_post():
    if request.method == 'GET':
        boards = BoardModel.query.order_by(BoardModel.priority.desc()).all()
        return render_template("front/public_post.html", boards=boards)
    else:
        form = PublicPostForm(request.form)
        if form.validate():
            title = form.title.data
            content = form.content.data
            board_id = form.board_id.data
            try:
                # get方法：接收一个id作为参数，如果找到了，那么会返回这条数据
                # 如果没有找到，那么会抛出异常
                board = BoardModel.query.get(board_id)
            except Exception as e:
                return restful.params_error(message="板块不存在！")
            post_model = PostModel(title=title, content=content, board=board, author=g.user)
            db.session.add(post_model)
            db.session.commit()
            return restful.ok(data={"id": post_model.id})
        else:
            return restful.params_error(message=form.messages[0])


@bp.post("/post/image/upload")
@login_required
def upload_image():
    form = UploadimageForm(formdata=request.files)  # 修改初始化方式
    if form.validate():
        image = form.image.data
        filename = image.filename
        _, ext = os.path.splitext(filename)
        filename = md5((g.user.email + str(time.time())).encode('utf-8')).hexdigest() + ext
        image_path = os.path.join(current_app.config['POST_IMAGE_SAVE_PATH'], filename)
        image.save(image_path)
        return jsonify({"errno": 0,
                        "data": [{"url": url_for("media.get_post_image", filename=filename),
                                  "alt": filename,
                                  "href": ""}]});
    else:
        message = form.messages[1]
        return restful.params_error(message=message)


# @bp.get("/post/detail/<post_id>")
# def post_detail(post_id):
#     post_model = PostModel.query.get(post_id)
#     if not post_model:
#         return restful.params_error(message='帖子不存在')
#     return render_template("front/post_detail.html", post=post_model,user=g.user)

@bp.get("/post/detail/<int:post_id>")
def post_detail(post_id):
    try:
        post_model = PostModel.query.get(post_id)
        collect = CollectModel.query.filter_by(user_id=g.user.id, post_id=post_id).first()
        if collect:
            message = "取消收藏"
        else:
            message = "收藏"
        collect_count = CollectModel.query.filter_by(post_id=post_id).count()
    except:
        return "404"
    comments_count = CommentModel.query.filter_by(post_id=post_id).count()
    context = {
        'post': post_model,
        'comments_count': comments_count,
        'message': message,
        'collect_count': collect_count
    }
    return render_template("front/post_detail.html", **context)


@bp.post("/comment")
@login_required
def public_comment():
    form = PublicCommentForm(request.form)
    if form.validate():
        content = form.content.data
        post_id = form.post_id.data
        try:
            post_model = PostModel.query.get(post_id)
        except Exception as e:
            return restful.params_error(message="帖子不存在！")
        comment = CommentModel(content=content, post_id=post_id, author_id=g.user.id)
        db.session.add(comment)
        db.session.commit()
        return restful.ok()
    else:
        message = form.messages[0]
        return restful.params_error(message=message)


# 收藏帖子
@bp.post("/post/collect")
@login_required
def collect_post():
    post_id = request.form.get("post_id")
    if not post_id:
        return restful.params_error(message="帖子ID不能为空")

    post = PostModel.query.get(post_id)
    if not post:
        return restful.params_error(message="帖子不存在")

    # 检查是否已收藏
    if g.user.has_collected(post_id):
        return restful.params_error(message="您已收藏过该帖子")

    # 新增收藏记录
    collect = CollectModel(user_id=g.user.id, post_id=post_id)
    db.session.add(collect)
    post.collects_count += 1  # 更新收藏数
    db.session.commit()
    return restful.ok(message="收藏成功")


# 取消收藏
@bp.post("/post/uncollect")
@login_required
def uncollect_post():
    post_id = request.form.get("post_id")
    if not post_id:
        return restful.params_error(message="帖子ID不能为空")

    post = PostModel.query.get(post_id)
    if not post:
        return restful.params_error(message="帖子不存在")

    collect = CollectModel.query.filter_by(user_id=g.user.id, post_id=post_id).first()
    if not collect:
        return restful.params_error(message="您未收藏过该帖子")

    db.session.delete(collect)
    post.collects_count -= 1  # 更新收藏数
    db.session.commit()
    return restful.ok(message="取消收藏成功")

@bp.route('/mypost')
@login_required
def myposts():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * current_app.config['POSTS_PER_PAGE']
    end = start + current_app.config['POSTS_PER_PAGE']

    posts = PostModel.query.filter_by(author_id=g.user.id).order_by(PostModel.create_time.desc()).slice(start, end)
    total = PostModel.query.filter_by(author_id=g.user.id).count()
    pagination = Pagination(bs_version=3, page=page, total=total, prev_label='上一页', next_label='下一页')
    return render_template("front/mypost.html", posts=posts, pagination=pagination)

@bp.route('/mycollect')
@login_required
def mycollect():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * current_app.config['POSTS_PER_PAGE']
    end = start + current_app.config['POSTS_PER_PAGE']

    # 使用join查询以获取帖子信息
    collects = CollectModel.query.filter_by(user_id=g.user.id).join(PostModel).order_by(CollectModel.create_time.desc()).slice(start, end).all()

    # 提取帖子信息
    posts = [collect.post for collect in collects]

    total = CollectModel.query.filter_by(user_id=g.user.id).count()
    pagination = Pagination(bs_version=3, page=page, total=total, prev_label='上一页', next_label='下一页')
    return render_template("front/mycollect.html", posts=posts, pagination=pagination)

@bp.post("post/delete")
def delete_post():
    post_id = request.form.get("id")
    try:
        post_model = PostModel.query.get(post_id)
    except Exception as e:
        return restful.server_error(message="帖子不存在")
    db.session.delete(post_model)
    db.session.commit()
    return restful.ok(message="删除成功")
# @bp.route('/base')
# def base():
#     return render_template("front/base.html")

# @bp.route('/index')
# def index():
#     if request.method == 'GET':
#         return render_template("front/base.html")

from flask import Blueprint
from datetime import datetime, timedelta
from flask_project.utils import restful
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_project.apps.cmsapi.froms import UploadImageForm, AddBannerForm, EditBannerForm
from flask_project.models.post import PostModel, CommentModel, BoardModel
import os
from flask import current_app, request, g
import time
from hashlib import md5
from flask_project.exts import db
from flask_project.models.auto import UserModel, Permission
from flask_project.models.post import BannerModel
from flask_project.exts import db
from sqlalchemy.sql import func
from .decorators import permission_required

bp = Blueprint('cmsapi', __name__, url_prefix='/cmsapi')


@bp.before_request
@jwt_required()
def cmsapi_before_request():
    if request.method == "OPTIONS":
        return
    identity = get_jwt_identity()
    user = UserModel.query.filter_by(id=identity).first()
    if user:
        setattr(g, 'user', user)



@bp.get("/")
@jwt_required()
def index():
    # 这个identity是当初从通过create_access_token传入的identity
    identity = get_jwt_identity()
    return restful.ok(message="success", data={"identity": identity})


# 轮播图post请求
@bp.post("/banner/image/upload")
@permission_required(Permission.BANNER)
def upload_banner_image():
    form = UploadImageForm(request.files)
    if form.validate():
        image = form.image.data
        # 不要使用用户上传上来的文件名，否则容易被黑客攻击
        filename = image.filename
        # xxx.png,xx.jpeg
        _, ext = os.path.splitext(filename)
        filename = md5((g.user.email + str(time.time())).encode("utf-8")).hexdigest() + ext
        image_path = os.path.join(current_app.config['BANNER_IMAGE_SAVE_PATH'], filename)
        image.save(image_path)
        return restful.ok(data={"image_url": filename})
    else:
        message = form.messages[0]
        return restful.params_error(message=message)


@bp.post("/banner/add")
def add_banner():
    form = AddBannerForm(request.form)
    if form.validate():
        name = form.name.data
        image_url = form.image_url.data
        link_url = form.link_url.data
        priority = form.priority.data
        banner_model = BannerModel(name=name, image_url=image_url, link_url=link_url, priority=priority)
        db.session.add(banner_model)
        db.session.commit()
        return restful.ok(data=banner_model.to_dict())
    else:
        return restful.params_error(message=form.messages[0])


@bp.get("/banner/list")
@permission_required(Permission.BANNER)
def get_banner_list():
    banners = BannerModel.query.order_by(BannerModel.create_time.desc()).all()
    banner_dicts = []
    for banner in banners:
        banner_dicts.append(banner.to_dict())
    return restful.ok(data=banner_dicts)


@bp.post("/banner/delete")
@permission_required(Permission.BANNER)
def delete_banner():
    banner_id = request.form.get("id")
    if not banner_id:
        return restful.params_error(message="缺少参数id")
    try:
        banner_model = BannerModel.query.filter_by(id=banner_id).first()
    except Exception as e:
        return restful.server_error(message="轮播图不存在")
    db.session.delete(banner_model)
    db.session.commit()
    return restful.ok(message="删除成功")


@bp.post("/banner/edit")
@permission_required(Permission.BANNER)
def edit_banner():
    form = EditBannerForm(request.form)
    if form.validate():
        banner_id = form.id.data
        try:
            banner_model = BannerModel.query.filter_by(id=banner_id).first()
        except Exception as e:
            return restful.server_error(message="轮播图不存在")
        name = form.name.data
        image_url = form.image_url.data
        link_url = form.link_url.data
        priority = form.priority.data
        banner_model.name = name
        banner_model.image_url = image_url
        banner_model.link_url = link_url
        banner_model.priority = priority
        db.session.commit()
        return restful.ok(data=banner_model.to_dict())
    else:
        return restful.params_error(message=form.messages[0])


@bp.get("post/list")
@permission_required(Permission.POST)
def get_post_list():
    page = request.args.get("page", default=1, type=int)
    per_page_count = current_app.config['POSTS_PER_PAGE']
    start = (page - 1) * per_page_count
    end = start + per_page_count
    query_obj = PostModel.query.order_by(PostModel.create_time.desc())
    total_count = query_obj.count()
    posts = query_obj.slice(start, end)
    post_list = [post.to_dict() for post in posts]
    return restful.ok(data={
        'post_list': post_list,
        'total_count': total_count,
        'page': page
    })


@bp.post("post/delete")
@permission_required(Permission.POST)
def delete_post():
    post_id = request.form.get("id")
    try:
        post_model = PostModel.query.get(post_id)
    except Exception as e:
        return restful.server_error(message="帖子不存在")
    db.session.delete(post_model)
    db.session.commit()
    return restful.ok(message="删除成功")


@bp.get('/comment/list')
@permission_required(Permission.COMMENT)
def comment_list():
    page = request.args.get("page", default=1, type=int)
    per_page_count = current_app.config['POSTS_PER_PAGE']
    start = (page - 1) * per_page_count
    end = start + per_page_count
    query_obj = CommentModel.query.order_by(CommentModel.create_time.desc())
    total_count = query_obj.count()
    comments = query_obj.slice(start, end)
    comment_list = [comment.to_dict() for comment in comments]
    return restful.ok(data={
        'comment_list': comment_list,
        'total_count': total_count,
        'page': page
    })


@bp.post('/comment/delete')
@permission_required(Permission.COMMENT)
def delete_comment():
    comment_id = request.form.get("id")
    try:
        comment_model = CommentModel.query.get(comment_id)
    except Exception as e:
        return restful.server_error(message="评论不存在")
    db.session.delete(comment_model)
    db.session.commit()
    return restful.ok(message="删除成功")


@bp.get("/user/list")
@permission_required(Permission.USER)
def user_list():
    page = request.args.get("page", default=1, type=int)
    per_page_count = current_app.config['POSTS_PER_PAGE']
    start = (page - 1) * per_page_count
    end = start + per_page_count
    total_count = UserModel.query.count()
    users = UserModel.query.slice(start, end).all()
    user_list = [user.to_dict() for user in users]

    return restful.ok(data={
        'user_list': user_list,
        'total_count': total_count,
        'page': page
    })


@bp.get('/user/staff')
@permission_required(Permission.USER)
def get_staff():
    page = request.args.get("page", default=1, type=int)
    per_page_count = current_app.config['POSTS_PER_PAGE']
    start = (page - 1) * per_page_count
    end = start + per_page_count
    total_count = UserModel.query.filter_by(is_staff=True).count()
    staffs = UserModel.query.filter_by(is_staff=True).slice(start, end).all()
    staff_list = [staff.to_dict() for staff in staffs]
    return restful.ok(data={
        'user_list': staff_list,
        'total_count': total_count,
        'page': page
    })


@bp.post("/user/active")
@permission_required(Permission.USER)
def active_user():
    is_active = request.form.get('is_active', type=int)
    user_id = request.form.get("id")
    user = UserModel.query.get(user_id)
    user.is_active = bool(is_active)
    db.session.commit()
    return restful.ok(data=user.to_dict())


@bp.post("/user/staff")
@permission_required(Permission.USER)
def staff_user():
    is_staff = request.form.get('is_staff', type=int)
    user_id = request.form.get("id")
    user = UserModel.query.get(user_id)
    user.is_staff = bool(is_staff)
    if user.is_staff == 0:
        user.role_id = None
    db.session.commit()
    return restful.ok(data=user.to_dict())


@bp.post("/user/role")
@permission_required(Permission.USER)
def changeRole():
    user_id = request.form.get("id")
    role_id = request.form.get("role_id")
    user = UserModel.query.get(user_id)
    user.role_id = role_id
    db.session.commit()
    return restful.ok(data=user.to_dict())


@bp.get("/board/list")
@permission_required(Permission.STAFF)
def board_list():
    page = request.args.get("page", default=1, type=int)
    per_page_count = current_app.config['POSTS_PER_PAGE']
    start = (page - 1) * per_page_count
    end = start + per_page_count
    total_count = BoardModel.query.count()
    boards = BoardModel.query.slice(start, end).all()
    board_list = [board.to_dict() for board in boards]
    return restful.ok(data={
        'board_list': board_list,
        'total_count': total_count,
        'page': page
    })
@bp.post("/board/add")
@permission_required(Permission.STAFF)
def add_board():
    name = request.form.get("name")
    priority = request.form.get("priority", type=int)
    board_model = BoardModel(name=name, priority=priority)
    db.session.add(board_model)
    db.session.commit()
    return restful.ok(data=board_model.to_dict())


@bp.post("/board/delete")
@permission_required(Permission.STAFF)
def delete_board():
    board_id = request.form.get("id")
    try:
        board_model = BoardModel.query.get(board_id)
    except Exception as e:
        return restful.server_error(message="板块不存在")
    db.session.delete(board_model)
    db.session.commit()
    return restful.ok(message="删除成功")

@bp.post("/board/edit")
@permission_required(Permission.STAFF)
def edit_board():
    name = request.form.get("name")
    priority = request.form.get("priority", type=int)
    board_id = request.form.get("id")
    try:
        board_model = BoardModel.query.get(board_id)
    except Exception as e:
        return restful.server_error(message="板块不存在")
    board_model.name = name
    board_model.priority = priority
    db.session.commit()
    return restful.ok(data=board_model.to_dict())


@bp.get("board/post/count")
def get_board_post_count():
    board_post_count_list = db.session.query(BoardModel.name, func.count(BoardModel.name)).join(PostModel).group_by(
        BoardModel.name).all()
    board_name = []
    post_count = []
    for board_post_count in board_post_count_list:
        board_name.append(board_post_count[0])
        post_count.append(board_post_count[1])
    return restful.ok(data={
        'board_name': board_name,
        'post_count': post_count
    })


@bp.get("/day7/post/count")
def day7_post_count():
    # 日期，帖子的数量
    # MySQL数据库：用的是date_format函数
    # SQlite数据库：用的是strfformat函数
    now = datetime.now()
    # 减6天，就是近7天的帖子
    # 时间的增、减
    # 一定要把时分秒毫秒都要减为0，不然就只能获取到7天前当前时间的帖子
    seven_day_ago = now - timedelta(days=6, hours=now.hour, minutes=now.minute, seconds=now.second,
                                    microseconds=now.microsecond)
    # [('2021-11-27', 99)]
    day7_post_count_list = db.session.query(func.date_format(PostModel.create_time, "%Y-%m-%d"),
                                            func.count(PostModel.id)).group_by(
        func.date_format(PostModel.create_time, "%Y-%m-%d")).filter(PostModel.create_time >= seven_day_ago).all()
    day7_post_count_dict = dict(day7_post_count_list)
    for x in range(7):
        date = seven_day_ago + timedelta(days=x)
        date_str = date.strftime("%Y-%m-%d")
        if date_str not in day7_post_count_dict:
            day7_post_count_dict[date_str] = 0
    dates = sorted(list(day7_post_count_dict.keys()))
    counts = []
    for date in dates:
        counts.append(day7_post_count_dict[date])
    data = {"dates": dates, "counts": counts}
    return restful.ok(data=data)

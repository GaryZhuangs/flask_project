from ..exts import db
from datetime import datetime
from sqlalchemy_serializer import SerializerMixin
class BoardModel(db.Model,SerializerMixin): # 定义板块模型
    serialize_only = ('id', 'name', 'priority', 'create_time')
    __tablename__ = 'board'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), unique=True)
    priority = db.Column(db.Integer, default=1)
    create_time = db.Column(db.DateTime, default=datetime.now)

class PostModel(db.Model, SerializerMixin): # 定义帖子模型
    serialize_only = ("id", "title", "content", "create_time", "board", "author","collects_count")
    __tablename__ = "post"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    board_id = db.Column(db.Integer, db.ForeignKey("board.id"))
    author_id = db.Column(db.String(100), db.ForeignKey("user.id"))
    board = db.relationship("BoardModel", backref=db.backref("posts"))
    author = db.relationship("UserModel", backref=db.backref("posts"))
    likes=db.Column(db.Integer,default=0)
    collects_count = db.Column(db.Integer, default=0)  # 收藏总数 collects_count = db.Column(db.Integer, default=0)  # 收藏总数

class BannerModel(db.Model, SerializerMixin): # 定义轮播图模型
    __tablename__ = 'banner'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    link_url = db.Column(db.String(255), nullable=False)
    priority = db.Column(db.Integer, default=0)
    create_time = db.Column(db.DateTime, default=datetime.now)


class CommentModel(db.Model, SerializerMixin): # 定义评论模型
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    author_id = db.Column(db.String(100), db.ForeignKey("user.id"), nullable=False)

    post = db.relationship("PostModel", backref=db.backref('comments', order_by="CommentModel.create_time.desc()",
                                                           cascade="delete, delete-orphan"))
    author = db.relationship("UserModel", backref='comments')


class CollectModel(db.Model, SerializerMixin): # 定义收藏模型
    __tablename__ = "collect"
    serialize_rules = ("-user", "-post")  # 避免循环引用
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 收藏id
    user_id = db.Column(db.String(100), db.ForeignKey("user.id"))  # 用户外键
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))      # 帖子外键
    create_time = db.Column(db.DateTime, default=datetime.now)      # 收藏时间

    # 关系字段（反向引用）
    user = db.relationship("UserModel", backref=db.backref("collects"))
    post = db.relationship("PostModel", backref=db.backref("collects"))



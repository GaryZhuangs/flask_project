from flask_project.exts import db
import shortuuid
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy_serializer import SerializerMixin
from .post import CollectModel
class Permission(object):
    # 255的二进制方式来表示 1111 1111
    ALL_PERMISSION = 0b11111111
    # 1. 访问者权限
    VISITOR =        0b00000001
    # 2. 管理帖子权限
    POST =         0b00000010
    # 3. 管理评论的权限
    COMMENT =      0b00000100
    # 4. 管理板块的权限
    BANNER =        0b00001000
    # 5. 管理前台用户的权限
    USER =      0b00010000
    # 6. 管理后台管理员的权限
    STAFF =        0b01000000
    # 7. 管理系统设置的权限

class RoleModel(db.Model, SerializerMixin):
    serialize_only = ("id", "name", "desc", "create_time")
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.String(200),nullable=True)
    create_time = db.Column(db.DateTime,default=datetime.now)
    permissions = db.Column(db.Integer,default=Permission.VISITOR)

class UserModel(db.Model, SerializerMixin):
    serialize_rules = ('-_password',"-posts",'-comments')
    # serialize_only = ('id', 'email', 'username', 'avatar','signature', 'join_time', 'is_staff', 'is_active')
    __tablename__ = 'user'
    # 定义用户表的字段
    id = db.Column(db.String(100), primary_key=True, default=shortuuid.uuid)  # 用户ID，主键，默认生成短UUID
    email = db.Column(db.String(50), nullable=False, unique=True)  # 用户邮箱，不允许为空且唯一
    username = db.Column(db.String(50), nullable=False)  # 用户名，不允许为空
    _password = db.Column(db.String(200), nullable=False)  # 用户密码，不允许为空
    # real_name = db.Column(db.string(50))  # 用户真实姓名
    avatar = db.Column(db.String(100))  # 用户头像URL
    signature = db.Column(db.String(100))  # 用户签名
    # gender=db.Column(db.Enum(GenderEnum),default=GenderEnum.UNKNOWN)  # 用户性别，默认未知
    join_time = db.Column(db.DateTime, default=datetime.now)  # 用户加入时间，默认当前时间
    is_staff = db.Column(db.Boolean, default=False)  # 是否为员工，默认否
    is_active = db.Column(db.Boolean, default=True)  # 用户是否激活，默认激活
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))  # 用户角色ID，外键关联角色表
    role=db.relationship('RoleModel',backref='users')  # 反向引用，获取角色信息
    def __init__(self ,*args, **kwargs):
      if 'password' in kwargs:
          self.password=kwargs.get('password')
          kwargs.pop('password')
      super(UserModel, self).__init__(*args, **kwargs) #传递剩余参数给父类
    @property
    def password(self):
        return self._password
    @password.setter
    def password(self, new_password):
        self._password = generate_password_hash(new_password)
    def check_password(self, password):
        return check_password_hash(self._password, password)
    def has_permission(self, permission):
        return (self.role.permissions & permission) == permission
    def has_collected(self, post_id):
        return CollectModel.query.filter_by(user_id=self.id, post_id=post_id).first() is not None

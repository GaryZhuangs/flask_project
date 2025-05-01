from wtforms import Form, ValidationError
from wtforms.fields import StringField, PasswordField,IntegerField, FileField
from wtforms.validators import Email, Length, EqualTo, InputRequired
from flask_wtf.file import FileAllowed, FileSize
from flask_project.models.auto import UserModel
from flask_project.exts import cache
from flask import request

class BaseForm(Form):
    @property
    def messages(self):
        message_list = []
        if self.errors:
            for errors in self.errors.values():
                message_list.extend(errors)
        return message_list
class RegisterForm(BaseForm):
    # 如果使用了Email这个validator，那么就必须要安装email_validator
    # pip install email_validator
    email = StringField(validators=[Email(message="请输入正确的邮箱！")])
    email_captcha = StringField(validators=[Length(6, 6, message="请输入正确格式的邮箱！")])
    username = StringField(validators=[Length(3, 20, message="请输入正确长度的用户名！")])
    password = StringField(validators=[Length(6, 20, message="请输入正确长度的密码！")])
    repeat_password = StringField(validators=[EqualTo("password", message="两次密码不一致！")])
    graph_captcha = StringField(validators=[Length(4, 4, message="请输入正确长度的图形验证码！")])

    def validate_email(self, field):
        email = field.data
        user = UserModel.query.filter_by(email=email).first()
        if user:
            raise ValidationError(message="邮箱已经被注册！")

    def validate_email_captcha(self, field):
        email_captcha = field.data
        email = self.email.data
        cache_captcha = cache.get(email)
        if not cache_captcha or email_captcha != cache_captcha:
            raise ValidationError(message="邮箱验证码错误！")

    def validate_graph_captcha(self, field):
        key = request.cookies.get("captcha_key")
        cache_captcha = cache.get(key)
        graph_captcha = field.data
        if not cache_captcha or cache_captcha.lower() != graph_captcha.lower():
            raise ValidationError(message="图形验证码错误！")
class LoginForm(BaseForm):
    email = StringField(validators=[Email(message="请输入正确的邮箱！")])
    password = PasswordField(validators=[Length(6, 20, message="请输入正确长度的密码！")])
    remember = IntegerField()
class UploadAvatarForm(BaseForm):
    image = FileField(validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], message='只允许上传jpg,png,jpeg格式的文件！'),
        FileSize(max_size=5*1024*1024, message='文件大小不能超过5M！')
    ])
class UploadimageForm(BaseForm):
    image = FileField(validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], message='只允许上传jpg,png,jpeg格式的文件！'),
        FileSize(max_size=10*1024*1024, message='文件大小不能超过10M！')
    ])

class EditProfileForm(BaseForm):
    signature=StringField(validators=[Length(0, 200, message="签名不能超过200个字符！")])
    username = StringField(validators=[Length(3, 20, message="请输入正确长度的用户名！")])

class PublicPostForm(BaseForm):
    title = StringField(validators=[Length(min=3, max=200, message="帖子标题必须在3-200之间！")])
    content = StringField(validators=[InputRequired(message="请传入内容！")])
    board_id = IntegerField(validators=[InputRequired(message="请传入板块ID！")])


class PublicCommentForm(BaseForm):
    content = StringField(validators=[InputRequired(message="请传入内容！")])
    post_id = IntegerField(validators=[InputRequired(message="请传入帖子ID！")])

class PublicCommentForm(BaseForm):
    content = StringField(validators=[InputRequired(message="请传入内容！")])
    post_id = IntegerField(validators=[InputRequired(message="请传入帖子ID！")])

class ResetPasswordForm(BaseForm):
    email = StringField(validators=[Email(message="请输入正确的邮箱！")])
    email_captcha = StringField(validators=[Length(6, 6, message="请输入正确格式的邮箱！")])
    password = StringField(validators=[Length(6, 20, message="请输入正确长度的密码！")])
    repeat_password = StringField(validators=[EqualTo("password", message="两次密码不一致！")])
    graph_captcha = StringField(validators=[Length(4, 4, message="请输入正确长度的图形验证码！")])

    def validate_email(self, field):
        email = field.data
        user = UserModel.query.filter_by(email=email).first()
        if not user:
            raise ValidationError(message="邮箱未注册！")

    def validate_email_captcha(self, field):
        email_captcha = field.data
        email = self.email.data
        cache_captcha = cache.get(email)
        if not cache_captcha or email_captcha != cache_captcha:
            raise ValidationError(message="邮箱验证码错误！")

    def validate_graph_captcha(self, field):
        key = request.cookies.get("captcha_key")
        cache_captcha = cache.get(key)
        graph_captcha = field.data
        if not cache_captcha or cache_captcha.lower() != graph_captcha.lower():
            raise ValidationError(message="图形验证码错误！")
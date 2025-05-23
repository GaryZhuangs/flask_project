from functools import wraps
from flask import g
from flask_project. utils import restful


def permission_required(permission):
    def outter(func):
        @wraps(func)
        def inner(*args, **kwargs):
            user = getattr(g, "user")
            if not user:
                return restful.unlogin_error()
            if user.has_permission(permission):
                return func(*args, **kwargs)
            else:
                return restful.permission_error(message="您没有权限访问这个接口！")
        return inner
    return outter
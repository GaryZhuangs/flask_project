from flask import g, redirect, url_for
from functools import wraps

def login_required(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if hasattr(g, 'user'):
            return f(*args, **kwargs)  # 返回原始函数的结果
        else:
            return redirect(url_for('front.login'))
    return inner

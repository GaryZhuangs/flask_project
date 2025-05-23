# This file is used to define the extensions of the Flask application.
# flask_sqlalchemy is used to interact with the database.
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_caching import Cache
from flask_wtf.csrf import CSRFProtect
from flask_avatars import Avatars
from flask_jwt_extended import JWTManager
from flask_cors import CORS
db=SQLAlchemy()
cache=Cache()
mail=Mail()
csrf=CSRFProtect()
avatars=Avatars()
jwt=JWTManager()
cors=CORS()
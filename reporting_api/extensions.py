from flasgger import Swagger
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

jwt_manager = JWTManager()

cors = CORS()

db = SQLAlchemy()

swagger = Swagger(template_file='apis/doc/home.yml')

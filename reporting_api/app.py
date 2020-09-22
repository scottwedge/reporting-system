import os

from flask import Flask, got_request_exception
from flask_jwt_extended.exceptions import JWTExtendedException
from jwt.exceptions import PyJWTError
from werkzeug.exceptions import HTTPException

from .apis import urls
from .config.default_config import DefaultConfig
from .exceptions.service_exception import ServiceException
from .exceptions.system_exception import SystemException
from .extensions import cors, db, jwt_manager, swagger
from .logger.logger import logger

_default_instance_path = '%(instance_path)s/instance' % \
                         {'instance_path': os.path.dirname(os.path.realpath(__file__))}


def log_exception(sender, exception, **extra):
    if (isinstance(exception, ServiceException) or isinstance(exception, SystemException)) \
            and exception.error_code not in (100000, 100001, 300000, 900001) \
            or isinstance(exception, HTTPException) \
            or issubclass(type(exception), PyJWTError) \
            or issubclass(type(exception), JWTExtendedException):
        logger.console(exception)
        return
    logger.exception(exception)


def create_app(script_info=None, config=None, instance_path=_default_instance_path):
    app = Flask(__name__, instance_relative_config=True, instance_path=instance_path)
    configure_app(app)
    configure_extensions(app)
    # configure_error(app)
    configure_blueprint(app)

    return app


def configure_app(app, external_config=None):
    # default configs
    app.config.from_object(DefaultConfig)
    app.config.from_pyfile("dev.py")

    if os.environ.get('TESTING_CONFIG'):
        app.config.from_envvar('TESTING_CONFIG')
        return

    if os.environ.get('STAGING_CONFIG'):
        app.config.from_envvar('STAGING_CONFIG')
        return

    if os.environ.get('PRODUCTION_CONFIG'):
        app.config.from_envvar('PRODUCTION_CONFIG')
        return

    if os.environ.get('DEV_CONFIG'):
        app.config.from_envvar('DEV_CONFIG')
        return

    if external_config:
        if isinstance(external_config, str):
            app.config.from_envvar(external_config)
        elif isinstance(external_config, object):
            app.config.from_object(external_config)


def configure_error(app):
    got_request_exception.connect(log_exception, app)


def configure_extensions(app):
    db.init_app(app)

    jwt_manager.init_app(app)

    cors.init_app(app,
                  origins=app.config['CORS_ORIGINS'],
                  methods=app.config['CORS_METHODS'],
                  allow_headers=app.config['CORS_ALLOW_HEADERS'])

    if not os.environ.get('PRODUCTION_CONFIG'):
        swagger.init_app(app)


def configure_blueprint(app):
    urls.register_blueprint(app)

class DefaultConfig(object):
    DEBUG = True

    CORS_ORIGINS = ['*']
    CORS_METHODS = ['POST', 'GET', 'OPTIONS', 'DELETE', 'PATCH', 'PUT']
    CORS_ALLOW_HEADERS = ['Authorization', 'Content-Type']

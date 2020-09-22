SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://abs_wms:GpBcYCmX5ZSaYFRi@192.168.0.173:3306/abs_wms'
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_ECHO = True

JWT_SECRET_KEY = 'personnel-system'
JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 3

# jwt 配置 如果不配置则使用 JWTManager默认值
JWT_TOKEN_LOCATION = ['cookies']  # jwt 传输方式改为cookie
JWT_COOKIE_SAMESITE = 'Strict'  # 严格禁止跨站传输，防止CSRF攻击（SPA前端用户体验还行，不影响，安全最重要！）

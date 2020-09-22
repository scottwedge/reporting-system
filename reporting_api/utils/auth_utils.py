from flask_jwt_extended import get_jwt_identity
from passlib.hash import pbkdf2_sha256 as sha256


def verify_hash(password, password_hash):
    """校验密码是否正确"""
    return sha256.verify(password, password_hash)


def generate_hash(password):
    """密码加密"""
    return sha256.hash(password)


def get_user_id():
    return get_jwt_identity()

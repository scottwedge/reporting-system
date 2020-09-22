from flask import session, request, render_template, redirect, jsonify
from flask_jwt_extended import create_access_token, jwt_required, create_refresh_token, set_access_cookies, \
    set_refresh_cookies, fresh_jwt_required, jwt_refresh_token_required
from flask_restful import Resource

from ..utils.auth_utils import verify_hash, generate_hash, verify_hash, get_user_id
from ..utils.requests_utils import get_argument
from ..utils.response_utils import ok, db_commit
from ..models.admin import AdminModel
from ..exceptions.service_error import ServiceError
from ..exceptions.service_exception import ServiceException
from ..extensions import jwt_manager, db


class Register(Resource):
    def post(self):
        username = request.form.get('username')
        password = request.form.get('password')
        password = generate_hash(password)

        u = AdminModel.query.filter_by(username=username).first()
        if u is not None:
            return jsonify({'result': '该同用户名已存在'})
        uu = AdminModel(username=username, password=password)

        db.session.add(uu)
        db.session.commit()

        token = create_access_token(identity=uu.id, fresh=True)
        refresh_token = create_refresh_token(identity=uu.id)

        data = {
            "access_token": token,
            "": refresh_token,
            "result": 'register success',
            "code": 200
        }

        resp = jsonify(data)
        set_access_cookies(response=resp, encoded_access_token=token)
        set_refresh_cookies(response=resp, encoded_refresh_token=refresh_token)
        return resp


class AdminLogin(Resource):
    def get(self):
        return ok()

    # @jwt_required
    def post(self):
        username = get_argument('username')
        password = get_argument('password')
        user = AdminModel.query.filter_by(username=username).first()
        if not user:
            raise ServiceException(ServiceError.NO_AUTH)

        if verify_hash(password, user.password):
            token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            data = {
                "access_token": token,
                "refresh_token": refresh_token,
                # "message": 'welcome login ',
                "username": user.username,
            }
            resp = jsonify(data)
            set_access_cookies(response=resp, encoded_access_token=token)
            set_refresh_cookies(response=resp, encoded_refresh_token=refresh_token)
            return ok(data)

        else:
            raise ServiceException(ServiceError.WRONG_PASSWORD)


class RefreshToken(Resource):
    @jwt_refresh_token_required
    def post(self):
        """刷新Token"""
        user = AdminModel.query.filter_by(id=get_user_id()).first()
        if user:
            return ok({'access_token': create_access_token(identity=user.id)})
        raise ServiceException(ServiceError.ADMIN_NOT_EXISTS)

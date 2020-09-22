from jwt.exceptions import *

noauth_errors = [
    InvalidTokenError, DecodeError, InvalidAudienceError, InvalidIssuerError,
    InvalidIssuedAtError, ImmatureSignatureError, InvalidKeyError,
    InvalidAlgorithmError, MissingRequiredClaimError
]


def monkey_patch(noauth_code, expire_code):
    for error in noauth_errors:
        error.error_code = noauth_code
    ExpiredSignatureError.error_code=expire_code

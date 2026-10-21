from urllib.parse import urlencode
import requests
from django.conf import settings
import base64
import json
import jwt


# used to create the SSO login url (first one)
def build_authorize_url(state):
    params = {
        "client_id": settings.OIDC_RP_CLIENT_ID,
        "redirect_uri": settings.OIDC_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid",
        "state": state,
    }
    return settings.OIDC_OP_AUTHORIZATION_ENDPOINT + "?" + urlencode(params)


# client ask from server to exchange the code for tokens (second one) (like getting letter)
def exchange_code_for_tokens(code):
    response = requests.post(
        settings.OIDC_OP_TOKEN_ENDPOINT,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.OIDC_REDIRECT_URI,
            "client_id": settings.OIDC_RP_CLIENT_ID,
            "client_secret": settings.OIDC_RP_CLIENT_SECRET,
        },
        timeout=10,
    )
    return response.json()


# in this step this is like checking that letter authenticity and getting the user info from it
def verify_id_token(id_token):
    header = jwt.get_unverified_header(id_token)
    jwks = requests.get(settings.OIDC_OP_JWKS_ENDPOINT, timeout=10).json()

    signing_key = None
    for key in jwks["keys"]:
        if key["kid"] == header["kid"] and key.get("alg") == "RS256":
            signing_key = jwt.PyJWK(key)

    if signing_key is None:
        raise jwt.InvalidTokenError("No matching signing key in JWKS")

    return jwt.decode(
        id_token,
        signing_key,
        algorithms=["RS256"],
        audience=settings.OIDC_RP_CLIENT_ID,
        issuer=settings.OIDC_OP_ISSUER,
    )

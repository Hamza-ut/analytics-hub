from urllib.parse import urlencode
from django.conf import settings
import requests
import hashlib
import base64
import jwt


# Builds the "go log in at Keycloak" link the browser is sent to.
def build_authorize_url(state, nonce, code_challenge):
    params = {
        "client_id": settings.OIDC_API_RP_CLIENT_ID,  # who is asking: our app
        "redirect_uri": settings.OIDC_API_REDIRECT_URI,  # where Keycloak sends the browser back
        "response_type": "code",  # "give me a one-time ticket (code)"
        "scope": "openid",  # "this is a login"
        "state": state,  # comes back in the callback URL
        "nonce": nonce,  # comes back inside the id_token
        "code_challenge": code_challenge,  # fingerprint of our secret word (PKCE)
        "code_challenge_method": "S256",  # how the fingerprint was made
    }
    return settings.OIDC_API_OP_AUTHORIZATION_ENDPOINT + "?" + urlencode(params)


# PKCE: turns the secret word into its fingerprint (SHA-256, base64url, no "=").
def make_code_challenge(code_verifier):
    as_bytes = code_verifier.encode()  # text → bytes
    fingerprint = hashlib.sha256(as_bytes).digest()  # bytes → 32-byte fingerprint
    as_text = base64.urlsafe_b64encode(fingerprint).decode()  # bytes → URL-safe text
    return as_text.rstrip("=")  # drop the "=" padding at the end


# Server-to-server call to Keycloak: trade the ticket (code) for tokens.
def exchange_code_for_tokens(code, code_verifier):
    response = requests.post(
        settings.OIDC_API_OP_TOKEN_ENDPOINT,
        data={
            "grant_type": "authorization_code",
            "code": code,  # the ticket from the callback URL
            "redirect_uri": settings.OIDC_API_REDIRECT_URI,
            "client_id": settings.OIDC_API_RP_CLIENT_ID,  # proves it's our app...
            "client_secret": settings.OIDC_API_RP_CLIENT_SECRET,  # ...with our app's password
            "code_verifier": code_verifier,  # the secret word; Keycloak checks it matches the fingerprint
        },
        timeout=10,
    )
    return response.json()  # Keycloak's answer: tokens, or an "error"


# Proves the id_token (the "letter") really comes from our Keycloak, then returns its contents.
def verify_id_token(id_token):
    header = jwt.get_unverified_header(id_token)  # which key signed it ("kid")
    jwks = requests.get(
        settings.OIDC_API_OP_JWKS_ENDPOINT, timeout=10
    ).json()  # Keycloak's public keys

    # pick the public key that matches the token's kid
    signing_key = None
    for key in jwks["keys"]:
        if key["kid"] == header["kid"] and key.get("alg") == "RS256":
            signing_key = jwt.PyJWK(key)

    if signing_key is None:
        raise jwt.InvalidTokenError("No matching signing key in JWKS")

    # checks signature + aud + iss + exp; raises an error if any fail, else returns the claims dict
    return jwt.decode(
        id_token,
        signing_key,
        algorithms=["RS256"],
        audience=settings.OIDC_API_RP_CLIENT_ID,
        issuer=settings.OIDC_API_OP_ISSUER,
    )


# Builds the "log out at Keycloak too" link the browser is sent to.
def build_logout_url(id_token):
    params = {
        "id_token_hint": id_token,  # proves which login is being ended
        "post_logout_redirect_uri": settings.OIDC_API_POST_LOGOUT_REDIRECT_URI,  # where to come back to
    }
    return settings.OIDC_API_OP_LOGOUT_ENDPOINT + "?" + urlencode(params)

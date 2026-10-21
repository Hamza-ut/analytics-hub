import secrets

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import AuthenticationForm

from .oidc import (
    build_authorize_url,
    exchange_code_for_tokens,
    verify_id_token,
    make_code_challenge,
)
import jwt


# 2. Redirect Target / Profile View
def simple_redirect_page(request):
    return render(request, "sso_experiment/simple_redirect.html")


# 1. Standard Login Page
def session_based(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Redirect to the named URL route 'redirect_page' (NOT a filename)
            return redirect("sso_experiment:redirect_page")
    else:
        form = AuthenticationForm()

    return render(request, "sso_experiment/login.html", {"form": form})


# SSO step 1: the "Sign in with University account" button lands here.
# Makes three random one-time values, remembers them in the session, sends the browser to Keycloak.
def oidc_based(request):
    state = secrets.token_urlsafe(32)  # checked in the callback URL
    oidc_nonce = secrets.token_urlsafe(32)  # checked inside the id_token
    code_verifier = secrets.token_urlsafe(64)  # PKCE secret word, never leaves our server

    request.session["oidc_state"] = state
    request.session["oidc_nonce"] = oidc_nonce
    request.session["oidc_code_verifier"] = code_verifier

    code_challenge = make_code_challenge(code_verifier)  # only the fingerprint goes in the URL

    return redirect(build_authorize_url(state, oidc_nonce, code_challenge))


# SSO step 2: Keycloak sends the browser back here with ?state=...&code=...
# Check → exchange → verify → check → find user → log in. Any failure stops the login.
def oidc_callback(request):
    # 1. is this the login this browser started? (pop = single use)
    returned_state = request.GET.get("state")
    saved_state = request.session.pop("oidc_state", None)

    if not saved_state or returned_state != saved_state:
        return HttpResponse("State mismatch: login rejected", status=400)

    # 2. trade the ticket (code) + our secret word for tokens
    code = request.GET.get("code")
    code_verifier = request.session.pop("oidc_code_verifier", None)

    if not code_verifier:
        return HttpResponse("Code verifier not found", status=400)

    tokens = exchange_code_for_tokens(code, code_verifier)

    # 3. prove the id_token is genuine and get its contents (claims)
    try:
        claims = verify_id_token(tokens["id_token"])
    except jwt.InvalidTokenError as error:
        return HttpResponse(f"Invalid ID token: {error}", status=400)

    # 4. was this token made for this exact login?
    returned_nonce = claims.get("nonce")
    saved_nonce = request.session.pop("oidc_nonce", None)

    if not saved_nonce or returned_nonce != saved_nonce:
        return HttpResponse("Nonce mismatch: login rejected", status=400)

    # 5. Keycloak says who it is; only existing, active Django users may enter
    username = claims.get("preferred_username", "").lower()

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponse(f"No account for '{username}' in this app.", status=403)

    if not user.is_active:
        return HttpResponse("This account is disabled.", status=403)

    # 6. normal Django login: creates the session + digibio_sid cookie
    login(request, user)

    return redirect("sso_experiment:redirect_page")

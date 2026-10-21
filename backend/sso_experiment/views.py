import secrets

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import AuthenticationForm

from .oidc import build_authorize_url, exchange_code_for_tokens, verify_id_token
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


# oidc login
def oidc_based(request):
    state = secrets.token_urlsafe(32)
    request.session["oidc_state"] = state
    return redirect(build_authorize_url(state))


# oidc callback
def oidc_callback(request):
    returned_state = request.GET.get("state")
    saved_state = request.session.pop("oidc_state", None)

    if not saved_state or returned_state != saved_state:
        return HttpResponse("State mismatch: login rejected", status=400)

    code = request.GET.get("code")
    tokens = exchange_code_for_tokens(code)
    try:
        claims = verify_id_token(tokens["id_token"])
    except jwt.InvalidTokenError as error:
        return HttpResponse(f"Invalid ID token: {error}", status=400)

    username = claims.get("preferred_username", "").lower()

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponse(f"No account for '{username}' in this app.", status=403)

    if not user.is_active:
        return HttpResponse("This account is disabled.", status=403)

    login(request, user)

    return redirect("sso_experiment:redirect_page")

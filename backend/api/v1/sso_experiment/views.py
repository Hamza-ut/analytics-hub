from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token, settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


from api.v1.accounts.serializers import UserLoginSerializer
from sso_experiment.oidc import (
    build_authorize_url,
    make_code_challenge,
    exchange_code_for_tokens,
    verify_id_token,
)

from django.shortcuts import redirect
from django.http import HttpResponse
import secrets
import jwt


class Login(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]
            user = authenticate(username=username, password=password)
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                return Response(
                    {
                        "token": token.key,
                        "user_id": user.pk,
                        "username": user.username,
                        "email": user.email,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"error": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SSOLogin(APIView):

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        state = secrets.token_urlsafe(32)  # checked in the callback URL
        oidc_nonce = secrets.token_urlsafe(32)  # checked inside the id_token
        code_verifier = secrets.token_urlsafe(
            64
        )  # PKCE secret word, never leaves our server

        request.session["oidc_state"] = state
        request.session["oidc_nonce"] = oidc_nonce
        request.session["oidc_code_verifier"] = code_verifier

        code_challenge = make_code_challenge(
            code_verifier
        )  # only the fingerprint goes in the URL

        return redirect(build_authorize_url(state, oidc_nonce, code_challenge))


class SSOCallback(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):  # GET: Keycloak redirects the BROWSER here
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

        # 6. NEW ENDING (instead of login() + redirect): hand out a DRF token
        token, _ = Token.objects.get_or_create(user=user)
        return redirect(f"{settings.FRONTEND_URL}/sso-landing?token={token.key}")

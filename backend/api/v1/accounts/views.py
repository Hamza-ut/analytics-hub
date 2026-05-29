from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication, SessionAuthentication

from django.contrib.auth import authenticate

from .serializers import UserRegistrationSerializer, UserLoginSerializer


@api_view(["POST"])  # This tells Django: "Only allow POST requests here"
def signup(request):
    # 1. Take the JSON data from the request
    serializer = UserRegistrationSerializer(data=request.data)

    # 2. Check if the data is valid (just like form.is_valid())
    if serializer.is_valid():
        # 3. Save the user (this calls the create() method we wrote in the serializer)
        serializer.save()

        # 4. Return JSON success message + the user data
        return Response(
            {"message": "User created successfully!", "user": serializer.data},
            status=status.HTTP_201_CREATED,
        )

    # 5. If it's NOT valid, return JSON errors (e.g., "Username already exists"), no message with this return as it takes from serializer.errors
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if serializer.is_valid():
        # WE DO NOT USE .save() HERE!
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        # 1. Authenticate the user
        user = authenticate(username=username, password=password)

        if user:
            # 2. Get or Create a Token for this user (it returns token and boolean)
            token, _ = Token.objects.get_or_create(user=user)

            # 3. Return the Token to the user
            return Response(
                {
                    "message": "Login successful!",
                    "token": token.key,
                    "user_id": user.pk,
                    "email": user.email,
                },
                status=status.HTTP_200_OK,
            )

        # This part handles if authenticate() fails (extra safety)
        return Response(
            {"error": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    # We simply find their token and delete it.
    request.user.auth_token.delete()

    return Response(
        {"message": "Logged out successfully. Token destroyed."},
        status=status.HTTP_200_OK,
    )


## ---------------------------------------------------------------- ##
## The below code is an alternative way to do the same thing using DRF's built-in generic views, but we wont use it for now
## ---------------------------------------------------------------- ##
# from rest_framework import generics
# class UserRegistrationAPIView(generics.CreateAPIView):
#     queryset = User.objects.all()  # Required by DRF, even if we won't use it directly
#     serializer_class = UserRegistrationSerializer

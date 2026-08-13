from rest_framework import serializers
from django.contrib.auth.models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(
        write_only=True
    )  # This means: "Don't include this in the output JSON, only use it for input"
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        ]

    # FIELD-LEVEL VALIDATION: Specifically for 'email'
    def validate_email(self, value):
        """Runs automatically because of the name starting with 'validate_'"""
        value = value.lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    # OBJECT-LEVEL VALIDATION: For comparing multiple fields
    def validate(self, data):
        """Runs automatically because of the name 'validate'"""
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError({"password1": "Passwords do not match."})
        return data

    # THE BUILDER: Only runs if all validation above passes and it creates validated_data dictionary
    def create(self, validated_data):
        """Runs automatically when you call serializer.save()"""
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            password=validated_data["password1"],
        )


class UserLoginSerializer(serializers.Serializer):
    # We just need to make sure these two pieces of data are provided
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

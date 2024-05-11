from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from django.contrib.auth.password_validation import validate_password

from .models import User, UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, required=True)

    # TODO: will add a validator to check if the student_number is authenticated

    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            # 'stduent_number' : {'required': True},
        }

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        # salt and hash the password
        user.set_password(validated_data['password'])
        user.save()
        # create a default user profile
        UserProfile.objects.create(user=user)

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ["real_name", "blog", "github",
                  "school", "major", "language", "username", "email"]

    def get_username(self, obj):
        return obj.username

    def get_email(self, obj):
        return obj.email


class EditUserProfileSerializer(serializers.ModelSerializer):
    real_name = serializers.CharField(
        max_length=32, allow_null=True, required=False)
    blog = serializers.URLField(
        max_length=256, allow_blank=True, required=False)
    github = serializers.URLField(
        max_length=256, allow_blank=True, required=False)
    school = serializers.CharField(
        max_length=64, allow_blank=True, required=False)
    major = serializers.CharField(
        max_length=64, allow_blank=True, required=False)
    language = serializers.CharField(
        max_length=32, allow_blank=True, required=False)

    class Meta:
        model = UserProfile
        fields = ["real_name", "blog", "github", "school", "major", "language"]

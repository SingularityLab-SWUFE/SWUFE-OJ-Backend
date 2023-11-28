from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User

from .models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2',
                  'email')
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()

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

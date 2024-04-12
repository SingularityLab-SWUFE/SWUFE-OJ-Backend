from django.db import models
from django.contrib.auth.models import AbstractBaseUser

from rest_framework_simplejwt.tokens import RefreshToken


class Role(object):
    REGULAR_USER = 'Regular User'
    ADMIN = 'Admin'
    SUPER_ADMIN = 'Super Admin'


class ProblemPermission(object):
    NONE = 'None'
    OWN = 'Own'
    ALL = 'All'


class UserManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, username):
        return self.get(**{f'{self.model.USERNAME_FIELD}__iexact': username})


class User(AbstractBaseUser):
    username = models.CharField(unique=True, max_length=255)
    email = models.TextField(null=True)
    # TODO: 将来考虑利用学号注册
    student_number = models.TextField(null=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True)
    
    admin_type = models.TextField(default=Role.REGULAR_USER)
    problem_permission = models.TextField(default=ProblemPermission.NONE)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = 'user'
        
    def get_token(self):
        return RefreshToken.for_user(self).access_token


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    real_name = models.TextField(null=True)
    blog = models.URLField(null=True)
    github = models.TextField(null=True)
    school = models.TextField(null=True)
    major = models.TextField(null=True)
    language = models.TextField(null=True)

    @property
    def username(self):
        return self.user.username

    @property
    def email(self):
        return self.user.email

    class Meta:
        db_table = "user_profile"

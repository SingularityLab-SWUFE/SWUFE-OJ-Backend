from django.db import models
from django.contrib.auth.models import User


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

from django.db import models
from account.models import User
from ckeditor.fields import RichTextField


class PostType(object):
    SOLUTION = 'Solution'
    HELP = 'Help'
    DISSCUSION = 'Discussion'


class Post(models.Model):
    title = models.TextField()
    content = RichTextField()
    post_type = models.CharField(max_length=20)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    post = models.ForeignKey(
        'Post', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # 递归外键, 允许评论关联到另一个评论
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'

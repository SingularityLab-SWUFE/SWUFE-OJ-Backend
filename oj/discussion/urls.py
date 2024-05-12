from django.urls import path
from .views import (PostViewAPI, PostUserAPI, CommentViewAPI, CommentUserAPI)

urlpatterns = [
    path('/post/<int:id>', PostViewAPI.as_view(), name='get_post'),
    path('/post', PostUserAPI.as_view(), name='user_posts_apis'),
    path('/comments', CommentViewAPI.as_view(), name='get_comments'),
    path('/comment/', CommentUserAPI.as_view(), name='user_comment_apis')
]

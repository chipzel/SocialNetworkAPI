from django.urls import path

from .views import (UserSignUpAPIView,
                    PostCreateView,
                    PostDetailView,
                    PostListView,
                    LikePostView,
                    AnalyticsView,
                    UserActivityAPIView)

app_name = 'api'

urlpatterns = [
    # user endpoints
    path('signup/', UserSignUpAPIView.as_view()),
    path('user/<int:user_id>', UserActivityAPIView.as_view()),
    # posts
    path('posts/', PostCreateView.as_view()),
    path('posts/<int:post_id>/', PostDetailView.as_view()),
    path('posts/all/', PostListView.as_view()),
    # like
    path('posts/<int:post_id>/like', LikePostView.as_view()),
    # analytics
    path('analytics/', AnalyticsView.as_view()),
]

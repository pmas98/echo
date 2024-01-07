from django.urls import path, include
from .views import (
    PostViewSet,
    CreatePostView,
    UserLoginView,
    UserRegistrationView,
    CheckAuthView,
    LogoutView,
    UserCommentsView,
    SpecificUserCommentView,
    PostCommentsView,
    SpecificPostCommentView,
    CreateCommentView,
    VoteView,
    UserPostsView,
    SpecificUserPostView,
    DeletePostView,
    DeleteCommentView,
    CombinedSearchView,
    UserLikedPostsView,
    UserDislikedPostsView,
    activate_account
)
urlpatterns = [
    path('posts/create/', CreatePostView.as_view(), name='create-task'),
    path('posts/', PostViewSet.as_view(), name='get-all-items'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('activate/<str:token>/', activate_account, name='activate'),
    path('auth/', CheckAuthView.as_view(), name='auth'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('posts/<int:user_id>/', UserPostsView.as_view(), name='user-posts'),
    path('posts/liked/<int:user_id>/', UserLikedPostsView.as_view(), name='user-posts'),
    path('posts/disliked/<int:user_id>/', UserDislikedPostsView.as_view(), name='user-posts'),
    path('posts/<int:user_id>/<int:pk>/', SpecificUserPostView.as_view(), name='specific-user-post'),
    path('posts/<int:pk>/delete/', DeletePostView.as_view(), name='delete-post'),
    path('posts/search/', CombinedSearchView.as_view(), name='search-posts'),
    path('comments/<int:pk>/delete/', DeleteCommentView.as_view(), name='delete-comment'),
    path('comments/user/<int:user_id>/', UserCommentsView.as_view(), name='user-comments'),
    path('comments/user/<int:user_id>/<int:pk>/', SpecificUserCommentView.as_view(), name='specific-user-comment'),
    path('comments/post/<int:post_id>/', PostCommentsView.as_view(), name='post-comments'),
    path('comments/post/<int:post_id>/<int:pk>/', SpecificPostCommentView.as_view(), name='specific-post-comment'),
    path('comments/create/', CreateCommentView.as_view(), name='create-comment'),
    path('vote/', VoteView.as_view(), name='vote'),

]
from django.urls import path
from .views import (
    PostListCreateView, PostDetailView, UserPostsView,
    feed_view, user_feed_view, like_post, unlike_post, toggle_like,
    search_posts, search_categories, search_tags, recommended_posts,
    TagListCreateView, TagDetailView,
    CategoryListCreateView, CategoryDetailView, category_posts,
    create_report, list_reports, update_report_status,
    admin_posts_list, admin_delete_post, admin_users_list, admin_toggle_user_active,
    debug_posts, publish_post, unpublish_post, publish_all_my_posts
)

urlpatterns = [
    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<str:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/user/<int:user_id>/', UserPostsView.as_view(), name='user-posts'),
    
    path('feed/', feed_view, name='feed'),
    path('feed/me/', user_feed_view, name='user-feed'),
    
    path('posts/<str:post_id>/like/', like_post, name='like-post'),
    path('posts/<str:post_id>/unlike/', unlike_post, name='unlike-post'),
    path('posts/<str:post_id>/toggle-like/', toggle_like, name='toggle-like'),
    path('posts/<str:post_id>/publish/', publish_post, name='publish-post'),
    path('posts/<str:post_id>/unpublish/', unpublish_post, name='unpublish-post'),
    path('posts/publish-all/', publish_all_my_posts, name='publish-all-my-posts'),
    
    path('search/', search_posts, name='search-posts'),
    path('search/categories/', search_categories, name='search-categories'),
    path('search/tags/', search_tags, name='search-tags'),
    path('recommended/', recommended_posts, name='recommended-posts'),
    
    path('tags/', TagListCreateView.as_view(), name='tag-list-create'),
    path('tags/<int:pk>/', TagDetailView.as_view(), name='tag-detail'),
    
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('categories/<int:category_id>/posts/', category_posts, name='category-posts'),
    
    path('reports/', create_report, name='create-report'),
    path('reports/list/', list_reports, name='list-reports'),
    path('reports/<int:report_id>/', update_report_status, name='update-report'),
    
    path('admin/posts/', admin_posts_list, name='admin-posts'),
    path('admin/posts/<str:post_id>/', admin_delete_post, name='admin-delete-post'),
    path('admin/users/', admin_users_list, name='admin-users'),
    path('admin/users/<int:user_id>/toggle-active/', admin_toggle_user_active, name='admin-toggle-user'),
    
    path('debug/', debug_posts, name='debug-posts'),
]


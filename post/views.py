from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import generics, status, views
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import Post, Tag, Category, Like, Report
from .serializers import (
    PostSerializer, PostListSerializer, TagSerializer, 
    CategorySerializer, LikeSerializer, ReportSerializer, 
    ReportCreateSerializer, UserBasicSerializer
)
from .recommendation import get_recommended_posts

class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostListSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        return Post.objects.filter(is_published=True).annotate(
            like_count=Count('likes')
        ).select_related('user', 'category').prefetch_related('tags')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostSerializer
        return PostListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return []

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, is_published=True)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.annotate(like_count=Count('likes'))

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated()]
        return []

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views += 1
        instance.save(update_fields=['views'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user and not self.request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to edit this post")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user and not self.request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to delete this post")
        instance.delete()

class UserPostsView(generics.ListAPIView):
    serializer_class = PostListSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return Post.objects.filter(
            user_id=user_id, 
            is_published=True
        ).annotate(
            like_count=Count('likes')
        ).select_related('user', 'category')

@api_view(['GET'])
def feed_view(request):
    sort_by = request.GET.get('sort', 'recent')
    
    queryset = Post.objects.filter(is_published=True).annotate(
        like_count=Count('likes')
    ).select_related('user', 'category')
    
    if sort_by == 'popular':
        queryset = queryset.order_by('-like_count', '-views', '-created_at')
    else:
        queryset = queryset.order_by('-created_at')
    
    paginator = StandardPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = PostListSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_feed_view(request):
    sort_by = request.GET.get('sort', 'recent')
    
    user = request.user
    if hasattr(user, 'actor') and user.actor.interests:
        user_interests = set(user.actor.interests.split(','))
        queryset = Post.objects.filter(
            Q(tags__name__in=user_interests) | Q(is_published=True),
            is_published=True
        ).distinct().annotate(
            like_count=Count('likes')
        ).select_related('user', 'category')
    else:
        queryset = Post.objects.filter(is_published=True).annotate(
            like_count=Count('likes')
        ).select_related('user', 'category')
    
    if sort_by == 'popular':
        queryset = queryset.order_by('-like_count', '-views', '-created_at')
    else:
        queryset = queryset.order_by('-created_at')
    
    paginator = StandardPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = PostListSerializer(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_post(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return Response({'detail': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
    
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    
    if created:
        serializer = LikeSerializer(like)
        return Response({
            'liked': True,
            'message': 'Post liked successfully',
            'like': serializer.data
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({
            'liked': True,
            'message': 'Post already liked'
        }, status=status.HTTP_200_OK)

@api_view(['DELETE', 'POST'])
@permission_classes([IsAuthenticated])
def unlike_post(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return Response({'detail': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        like = Like.objects.get(user=request.user, post=post)
        like.delete()
        return Response({
            'liked': False,
            'message': 'Post unliked successfully'
        }, status=status.HTTP_200_OK)
    except Like.DoesNotExist:
        return Response({
            'liked': False,
            'message': 'Post was not liked'
        }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_like(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return Response({'detail': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        like = Like.objects.get(user=request.user, post=post)
        like.delete()
        return Response({
            'liked': False,
            'message': 'Post unliked successfully'
        }, status=status.HTTP_200_OK)
    except Like.DoesNotExist:
        like = Like.objects.create(user=request.user, post=post)
        return Response({
            'liked': True,
            'message': 'Post liked successfully'
        }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def search_posts(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category')
    tag_names = request.GET.getlist('tags')
    
    queryset = Post.objects.filter(is_published=True)
    
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query)
        )
    
    if category_id:
        try:
            queryset = queryset.filter(category_id=int(category_id))
        except (ValueError, TypeError):
            pass
    
    if tag_names:
        for tag_name in tag_names:
            queryset = queryset.filter(tags__name__iexact=tag_name)
    
    queryset = queryset.distinct().annotate(
        like_count=Count('likes', distinct=True)
    ).select_related('user', 'category').prefetch_related('tags')
    
    paginator = StandardPagination()
    page = paginator.paginate_queryset(queryset, request)
    
    if page is not None:
        serializer = PostListSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
    serializer = PostListSerializer(queryset, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
def search_categories(request):
    query = request.GET.get('q', '')
    
    queryset = Category.objects.all()
    
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    paginator = StandardPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = CategorySerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
def search_tags(request):
    query = request.GET.get('q', '')
    
    queryset = Tag.objects.all()
    
    if query:
        queryset = queryset.filter(name__icontains=query)
    
    paginator = StandardPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = TagSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommended_posts(request):
    posts = get_recommended_posts(request.user)
    paginator = StandardPagination()
    page = paginator.paginate_queryset(posts, request)
    serializer = PostListSerializer(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)

class TagListCreateView(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = StandardPagination

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return []

class TagDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = StandardPagination

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return []

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            from .serializers import CategoryDetailSerializer
            return CategoryDetailSerializer
        from .serializers import CategorySerializer
        return CategorySerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated()]
        return []

@api_view(['GET'])
def category_posts(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return Response({'detail': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
    
    queryset = Post.objects.filter(
        category_id=category_id,
        is_published=True
    ).annotate(
        like_count=Count('likes')
    ).select_related('user', 'category').prefetch_related('tags')
    
    paginator = StandardPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = PostListSerializer(page, many=True, context={'request': request})
    
    response_data = paginator.get_paginated_response(serializer.data)
    response_data.data['category'] = {
        'id': category.id,
        'name': category.name,
        'description': category.description
    }
    return response_data

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_report(request):
    serializer = ReportCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(reporter=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_reports(request):
    status_filter = request.GET.get('status', 'pending')
    reports = Report.objects.filter(status=status_filter).select_related(
        'reporter', 'post', 'reviewed_by'
    )
    
    paginator = StandardPagination()
    page = paginator.paginate_queryset(reports, request)
    serializer = ReportSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def update_report_status(request, report_id):
    try:
        report = Report.objects.get(pk=report_id)
    except Report.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    new_status = request.data.get('status')
    if new_status not in dict(Report.STATUS_CHOICES):
        return Response({'detail': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
    
    report.status = new_status
    report.reviewed_by = request.user
    report.reviewed_at = timezone.now()
    report.save()
    
    serializer = ReportSerializer(report)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_posts_list(request):
    queryset = Post.objects.all().annotate(
        like_count=Count('likes'),
        report_count=Count('reports')
    ).select_related('user', 'category')
    
    paginator = StandardPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = PostListSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def admin_delete_post(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_users_list(request):
    users = User.objects.all().annotate(
        post_count=Count('posts'),
        like_count=Count('likes'),
        report_count=Count('reports_made')
    )
    
    paginator = StandardPagination()
    page = paginator.paginate_queryset(users, request)
    serializer = UserBasicSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def admin_toggle_user_active(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        user.is_active = not user.is_active
        user.save()
        serializer = UserBasicSerializer(user)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def debug_posts(request):
    total_posts = Post.objects.count()
    published_posts = Post.objects.filter(is_published=True).count()
    unpublished_posts = Post.objects.filter(is_published=False).count()
    
    return Response({
        'total_posts': total_posts,
        'published_posts': published_posts,
        'unpublished_posts': unpublished_posts,
        'posts': list(Post.objects.values('id', 'title', 'is_published', 'user__username')[:10])
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def publish_post(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
        if post.user != request.user and not request.user.is_staff:
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        post.is_published = True
        post.save(update_fields=['is_published'])
        return Response({'message': 'Post published successfully', 'is_published': True})
    except Post.DoesNotExist:
        return Response({'detail': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unpublish_post(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
        if post.user != request.user and not request.user.is_staff:
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        post.is_published = False
        post.save(update_fields=['is_published'])
        return Response({'message': 'Post unpublished successfully', 'is_published': False})
    except Post.DoesNotExist:
        return Response({'detail': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def publish_all_my_posts(request):
    updated = Post.objects.filter(user=request.user, is_published=False).update(is_published=True)
    return Response({
        'message': f'Published {updated} posts successfully',
        'count': updated
    })


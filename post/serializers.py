from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Tag, Category, Like, Report

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = '__all__'

    def get_post_count(self, obj):
        return obj.posts.filter(is_published=True).count()

class CategoryDetailSerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()
    posts = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = '__all__'

    def get_post_count(self, obj):
        return obj.posts.filter(is_published=True).count()

    def get_posts(self, obj):
        from django.db.models import Count
        posts = obj.posts.filter(is_published=True).annotate(
            like_count=Count('likes')
        ).select_related('user', 'category').prefetch_related('tags')[:20]
        return PostListSerializer(posts, many=True, context=self.context).data

class PostSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    like_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'updated_at', 'views')

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, post=obj).exists()
        return False

    def create(self, validated_data):
        tag_ids = validated_data.pop('tag_ids', [])
        post = Post.objects.create(**validated_data)
        if tag_ids:
            tags = Tag.objects.filter(id__in=tag_ids)
            post.tags.set(tags)
        return post

    def update(self, instance, validated_data):
        tag_ids = validated_data.pop('tag_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tag_ids is not None:
            tags = Tag.objects.filter(id__in=tag_ids)
            instance.tags.set(tags)
        return instance

class PostListSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    like_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'user', 'title', 'category', 'category_name', 'created_at', 'views', 'like_count', 'image')

class LikeSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)

    class Meta:
        model = Like
        fields = '__all__'
        read_only_fields = ('user', 'created_at')

class ReportSerializer(serializers.ModelSerializer):
    reporter = UserBasicSerializer(read_only=True)
    reviewed_by = UserBasicSerializer(read_only=True)
    post_title = serializers.CharField(source='post.title', read_only=True)

    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ('reporter', 'created_at', 'reviewed_at', 'reviewed_by')

class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ('post', 'reason', 'description')


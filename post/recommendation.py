from django.db.models import Count, Q
from collections import Counter
import math

def get_recommended_posts(user, limit=20):
    from .models import Post, Like
    
    liked_posts = Like.objects.filter(user=user).select_related('post')
    
    if not liked_posts.exists():
        return Post.objects.filter(is_published=True).annotate(
            like_count=Count('likes')
        ).order_by('-like_count', '-views')[:limit]
    
    user_interest_tags = set()
    user_interest_categories = []
    
    for like in liked_posts:
        post = like.post
        if post.category:
            user_interest_categories.append(post.category.id)
        user_interest_tags.update(post.tags.values_list('name', flat=True))
    
    if hasattr(user, 'actor') and user.actor.interests:
        actor_interests = user.actor.interests.split(',')
        user_interest_tags.update([interest.strip() for interest in actor_interests])
    
    liked_post_ids = [like.post.id for like in liked_posts]
    
    candidate_posts = Post.objects.filter(
        is_published=True
    ).exclude(
        id__in=liked_post_ids
    ).prefetch_related('tags').select_related('category')
    
    scored_posts = []
    for post in candidate_posts:
        score = calculate_similarity_score(
            post, 
            user_interest_tags, 
            user_interest_categories
        )
        if score > 0:
            scored_posts.append((post, score))
    
    scored_posts.sort(key=lambda x: x[1], reverse=True)
    
    recommended = [post for post, score in scored_posts[:limit]]
    
    if len(recommended) < limit:
        additional_posts = Post.objects.filter(
            is_published=True
        ).exclude(
            id__in=liked_post_ids + [p.id for p in recommended]
        ).annotate(
            like_count=Count('likes')
        ).order_by('-like_count', '-views')[:limit - len(recommended)]
        
        recommended.extend(additional_posts)
    
    return recommended

def calculate_similarity_score(post, user_tags, user_categories):
    score = 0.0
    
    post_tags = set(post.tags.values_list('name', flat=True))
    tag_intersection = len(user_tags.intersection(post_tags))
    tag_union = len(user_tags.union(post_tags))
    
    if tag_union > 0:
        tag_similarity = tag_intersection / tag_union
        score += tag_similarity * 10
    
    if post.category and post.category.id in user_categories:
        category_weight = user_categories.count(post.category.id) / len(user_categories)
        score += category_weight * 5
    
    like_count = post.likes.count() if hasattr(post, 'likes') else 0
    score += math.log1p(like_count) * 0.5
    
    score += math.log1p(post.views) * 0.3
    
    return score

def get_similar_posts(post, limit=10):
    similar_posts = Post.objects.filter(
        is_published=True
    ).exclude(
        id=post.id
    ).prefetch_related('tags').select_related('category')
    
    post_tags = set(post.tags.values_list('name', flat=True))
    post_category_list = [post.category.id] if post.category else []
    
    scored_posts = []
    for candidate in similar_posts:
        score = calculate_similarity_score(candidate, post_tags, post_category_list)
        if score > 0:
            scored_posts.append((candidate, score))
    
    scored_posts.sort(key=lambda x: x[1], reverse=True)
    return [post for post, score in scored_posts[:limit]]


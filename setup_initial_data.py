import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pororohub.settings')
django.setup()

from post.models import Category, Tag

def create_initial_categories():
    categories = [
        {'name': 'Technology', 'description': 'Posts about technology, programming, and software'},
        {'name': 'Science', 'description': 'Scientific discussions and discoveries'},
        {'name': 'Arts', 'description': 'Creative arts and design'},
        {'name': 'Education', 'description': 'Educational content and tutorials'},
        {'name': 'Entertainment', 'description': 'Movies, music, and entertainment'},
        {'name': 'Sports', 'description': 'Sports and fitness'},
        {'name': 'News', 'description': 'Current events and news'},
        {'name': 'General', 'description': 'General discussions'},
    ]
    
    for cat_data in categories:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created:
            print(f"Created category: {category.name}")
        else:
            print(f"Category already exists: {category.name}")

def create_initial_tags():
    tags = [
        'python', 'javascript', 'java', 'c++', 'tutorial',
        'beginner', 'advanced', 'web-development', 'mobile',
        'ai', 'machine-learning', 'data-science', 'cybersecurity',
        'cloud', 'devops', 'frontend', 'backend', 'fullstack',
        'react', 'vue', 'angular', 'django', 'flask',
        'nodejs', 'express', 'mongodb', 'postgresql', 'mysql',
        'docker', 'kubernetes', 'aws', 'azure', 'gcp'
    ]
    
    for tag_name in tags:
        tag, created = Tag.objects.get_or_create(name=tag_name)
        if created:
            print(f"Created tag: {tag.name}")
        else:
            print(f"Tag already exists: {tag.name}")

if __name__ == '__main__':
    print("Creating initial categories...")
    create_initial_categories()
    
    print("\nCreating initial tags...")
    create_initial_tags()
    
    print("\nInitial data setup complete!")


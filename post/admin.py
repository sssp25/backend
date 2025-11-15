from django.contrib import admin
from .models import Post, Tag, Category, Like, Report

admin.site.register(Post)
admin.site.register(Tag)
admin.site.register(Category)
admin.site.register(Like)
admin.site.register(Report)


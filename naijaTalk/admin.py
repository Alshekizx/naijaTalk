from django.contrib import admin

from .models import NewsCategory, NewsArticle, UserProfile

admin.site.register(UserProfile)
admin.site.register(NewsCategory)
admin.site.register(NewsArticle)
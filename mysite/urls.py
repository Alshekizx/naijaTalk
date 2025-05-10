from django.contrib import admin
from django.urls import path
from naijaTalk import views # type: ignore
from naijaTalk.auth_views import signup_view, login_view, logout_view


urlpatterns = [
    # Public site
    path('', views.index, name='home'),
     path('article/<int:pk>/comment/', views.article_add_comment, name='article_add_comment'),
    path('world-news/', views.world_news, name='world_news'),
    path('local-news/', views.local_news, name='local_news'),
    path('opinion/', views.opinion, name='opinion'),
    path('technology/', views.technology, name='technology'),
    path('entertainment/', views.entertainment, name='entertainment'),
    path('sport/', views.sport, name='sports'),

    path('subscribe/', views.subscribe, name='subscribe'),
    path('business/', views.business, name='business'),
    path('health-news/', views.health_news, name='health_news'),
    path('celebrity-news/', views.celebrity_news, name='celebrity_news'),
    
    # blog view
 
    path('article/<slug:slug>/', views.article_detail, name='article_detail'),
    # urls.py

    # For nav-item clicks
    path('category/<slug:category_slug>/', views.category_page, name='category_page'),

    # For top-category card clicks
    path('top-category/<slug:category_slug>/', views.category_news, name='category_news'),

    # Static pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # Error pages
    path('404/', views.error404, name='error404'),
    path('505/', views.error505, name='error505'),

    # Admin-style custom pages
    path('admin/ai-feed/', views.ai_feed, name='ai_feed'),
    path('admin/create-post/', views.create_post, name='create_post'),
    path('admin/edit-post/', views.edit_post, name='edit_post'),
    path('admin/settings/', views.settings, name='settings'),

    # Auth
    path('auth/sign_up/', views.signup_view, name='signup'),
    path('auth/login/', views.login_view, name='login'),
   
    path('logout/', views.logout_view, name='logout'), 

   
    # Django Admin
    path('admin/', admin.site.urls),
]
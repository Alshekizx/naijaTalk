from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, render, redirect
from .models import NewsCategory, NewsArticle, Comment
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
import random
from django.contrib.auth.decorators import login_required

# ==========================
# Utility Functions
# ==========================
def get_random_color():
    colors = ['#FF5733', '#33FF57', '#3357FF', '#F033FF', '#FF33A1', '#A1FF33']
    return random.choice(colors)


def get_top_categories(filter_kwargs=None):
    """
    Return list of categories with their latest article.
    Optionally filter articles using `filter_kwargs` (e.g., {'local_news': True}).
    """
    filter_kwargs = filter_kwargs or {}
    categories = NewsCategory.objects.all()
    top_categories = []

    for category in categories:
        latest_article = NewsArticle.objects.filter(category=category, **filter_kwargs).order_by('-published_date').first()
        if latest_article:
            category.latest_article = latest_article
            top_categories.append(category)

    return top_categories

def get_base_context():
    return {
        'breaking_news': NewsArticle.objects.order_by('-created_at')[:3],
        'latest_articles': NewsArticle.objects.all().order_by('-created_at')[:10],
        'categories': NewsCategory.objects.all(),
        'top_categories': get_top_categories(),
        'nav_items': get_nav_items(),
    }


def get_nav_items():
    static_items = [
        ('World News', '/'),
        ('Local News', '/local-news'),
    ]
    static_names = {name for name, _ in static_items}

    nav_items = static_items[:]
    for cat in NewsCategory.objects.all():
        if cat.name not in static_names:
            nav_items.append((cat.name, f'/category/{cat.slug}'))

    return nav_items

def get_absolute_url(self):
    return f'/article/{self.slug}/'

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


# ==========================
# General Views
# ==========================

def index(request):
    breaking_news = NewsArticle.objects.order_by('-created_at')[:3]
    latest_articles = NewsArticle.objects.all().order_by('-created_at')[:10]

    context = {
        'breaking_news': breaking_news,
        'latest_articles': latest_articles,
        'categories': NewsCategory.objects.all(),
        'top_categories': get_top_categories(),
        'nav_items': get_nav_items(),
        'random_color': get_random_color(),  # Include random_color in the context
    }

    return render(request, 'index.html', context)

def article_detail(request, slug):
    article = get_object_or_404(NewsArticle, slug=slug)
    comments = article.comments.select_related('user__profile').order_by('-created_at')  # reverse relation assumed as 'comments'

    return render(request, 'article_detail.html', {
        'article': article,
        'comments': comments,
    })

def category_news(request, category_slug):
    category = get_object_or_404(NewsCategory, slug=category_slug)
    articles = NewsArticle.objects.filter(category=category).order_by('-published_date')
    other_categories = NewsCategory.objects.exclude(id=category.id)

    top_categories = []
    for cat in other_categories:
        latest_article = NewsArticle.objects.filter(category=cat).order_by('-published_date').first()
        if latest_article:
            cat.latest_article = latest_article
            top_categories.append(cat)

    return render(request, 'category_news.html', {
        'category': category,
        'articles': articles,
        'top_categories': top_categories
    })


def category_page(request, category_slug):
    category = get_object_or_404(NewsCategory, slug=category_slug)
    articles = NewsArticle.objects.filter(category=category).order_by('-published_date')

    context = {
        'breaking_news': NewsArticle.objects.filter(category=category).order_by('-created_at')[:3],
        'latest_articles': articles[:10],
        'category': category,
        'articles': articles,
        'categories': [category],  # Only include the selected category
        'top_categories': [category],  # Optionally show only selected in top category
        'nav_items': get_nav_items(),  # This can still show all categories in nav
    }

    return render(request, 'category_page.html', context)



# ==========================
# Section Views
# ==========================

def local_news(request):
    breaking_news = NewsArticle.objects.filter(local_news=True).order_by('-created_at')[:3]
    latest_articles = NewsArticle.objects.filter(local_news=True).order_by('-created_at')[:10]

    context = {
        'breaking_news': breaking_news,
        'latest_articles': latest_articles,
        'categories': NewsCategory.objects.all(),
        'top_categories': get_top_categories({'local_news': True}),
        'nav_items': get_nav_items(),
    }
    return render(request, 'local_news.html', context)


def world_news(request): return render(request, 'news/world_news.html')
def opinion(request): return render(request, 'news/opinion.html')
def technology(request): return render(request, 'news/technology.html')
def entertainment(request): return render(request, 'news/entertainment.html')
def sport(request): return render(request, 'news/sport.html')
def health_news(request): return render(request, 'news/health_news.html')
def business(request): return render(request, 'news/business.html')
def celebrity_news(request): return render(request, 'news/celebrity_news.html')


# ==========================
# Static Pages
# ==========================

def subscribe(request): return render(request, 'news/subscribe.html')
def about(request): return render(request, 'page/about.html')
def contact(request): return render(request, 'page/contact.html')
def error404(request): return render(request, 'errors/404.html')
def error505(request): return render(request, 'error/505.html')


# ==========================
# Admin Views
# ==========================

def ai_feed(request): return render(request, 'admin/ai_feed.html')
def create_post(request): return render(request, 'admin/create_post.html')
def edit_post(request): return render(request, 'admin/edit_post.html')
def settings(request): return render(request, 'admin/settings.html')


# ==========================
# Authentication Views
# ==========================

def dashboard(request): return render(request, 'auth/dashboard.html')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirect to home if already logged in

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in after sign-up

            # Send a welcome email
           # send_mail(
           #     'Welcome to Our Website',
             #   'Thank you for signing up! We are happy to have you.',
             #   settings.EMAIL_HOST_USER,  # From email
            #    [user.email],  # To email
             #   fail_silently=False,
            #)

            return redirect('home')  # Change to your home view
    else:
        form = SignUpForm()
    
    return render(request, 'auth/sign_up.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirect to home if already logged in

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Send a login notification email
          
            return redirect('home')  # Redirect to the home view
        else:
            messages.error(request, 'Invalid credentials')  # Show error message
    else:
        form = AuthenticationForm()
    
    return render(request, 'auth/login.html', {'form': form})
def logout_view(request):
    logout(request)
    return redirect('login') 

@login_required
def article_add_comment(request, pk):
    article = get_object_or_404(NewsArticle, pk=pk)
    if request.method == 'POST':
        body = request.POST.get('body')
        Comment.objects.create(
            article=article,
            user=request.user,
            body=body
        )
    return redirect(article.get_absolute_url())


def signup_view(request):
    # after user is created
    user_profile = user.userprofile
    user_profile.signup_ip = get_client_ip(request)
    # Optionally get location from IP using GeoIP or external API
    user_profile.location = "Abuja, Nigeria"  # You can automate this
    user_profile.save()
#/naijaTalk/models.py

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.text import slugify



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    signup_ip = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return self.user.username


class NewsCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    last_fetched = models.DateTimeField(null=True, blank=True, default=None)  # <-- Add this line

    def __str__(self):
        return self.name

class NewsArticle(models.Model):
    title = models.CharField(max_length=200)
    summary = models.TextField()
    content = models.TextField()
    author = models.CharField(max_length=100)
    category = models.ForeignKey(NewsCategory, on_delete=models.CASCADE)
    published_date = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

    image_url = models.URLField(blank=True, null=True)
    image_url_2 = models.URLField(blank=True, null=True)
    image_url_3 = models.URLField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)

    slug = models.SlugField(unique=True)
    breaking_news = models.BooleanField(default=False)
    local_news = models.BooleanField(default=False)

    class Meta:
        ordering = ['-published_date']
        verbose_name = "News Article"
        verbose_name_plural = "News Articles"

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})
    
    def get_all_images(self):
        images = [img for img in [self.image_url, self.image_url_2, self.image_url_3] if img]
        if not images:
            return ['/static/images/default.jpeg'] * 3
        while len(images) < 3:
            images.append(images[len(images) % len(images)])
        return images

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Comment(models.Model):
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} on {self.article.title}"
    

    
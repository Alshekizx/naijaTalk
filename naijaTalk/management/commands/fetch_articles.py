# /naijaTalk/management/commands/fetch_articles.py

from django.core.management.base import BaseCommand
from newspaper import Article
from naijaTalk.models import NewsArticle, NewsCategory
from django.utils.text import slugify
from django.utils import timezone  # Import timezone from Django

class Command(BaseCommand):
    help = 'Fetch and save a single news article from a given URL'

    def add_arguments(self, parser):
        parser.add_argument('url', type=str, help='URL of the news article to fetch')
        parser.add_argument('--category', type=str, default='General', help='Category name for the article')

    def handle(self, *args, **kwargs):
        url = kwargs['url']
        category_name = kwargs['category']
        self.fetch_article_data(url, category_name)

    def fetch_article_data(self, url, category_name):
        try:
            article = Article(url)
            article.download()
            article.parse()
            article.nlp()

            category, _ = NewsCategory.objects.get_or_create(
                name=category_name,
                defaults={'slug': slugify(category_name)}
            )

            slug = slugify(article.title)
            if NewsArticle.objects.filter(slug=slug).exists():
                self.stdout.write(self.style.WARNING(f"Article '{article.title}' already exists."))
                return
            
            images = article.images if article.images else []
            image_list = list(images)[:3]
            while len(image_list) < 3:
                image_list.append(image_list[-1] if image_list else '')

            video_url = article.movies[0] if article.movies else None

            NewsArticle.objects.create(
                title=article.title,
                summary=article.summary,
                content=article.text,
                author=", ".join(article.authors) if article.authors else "Anonymous",
                category=category,
                published_date=article.publish_date.date() if article.publish_date else timezone.now().date(),  # Replace datetime.today() with timezone.now()
                image_url=image_list[0] if len(image_list) > 0 else '',
                image_url_2=image_list[1] if len(image_list) > 1 else '',
                image_url_3=image_list[2] if len(image_list) > 2 else '',
                video_url=video_url,
                slug=slug
            )

            self.stdout.write(self.style.SUCCESS(f"Saved article: {article.title}"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error fetching article from {url}: {e}"))
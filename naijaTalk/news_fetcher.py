# /naijaTalk/news_fetcher.py

import logging
from datetime import datetime, timedelta
from newspaper import Article
import feedparser
from naijaTalk.models import NewsArticle, NewsCategory
from django.utils.text import slugify
from django.utils import timezone  # Import timezone from Django

def fetch_articles_from_feed(category_name, feed_url):
    try:
        category, _ = NewsCategory.objects.get_or_create(
            name=category_name,
            defaults={'slug': slugify(category_name)}
        )

        # Use timezone.now() to ensure the datetime is timezone-aware
        last_fetched = category.last_fetched or timezone.now() - timedelta(days=1)  # Replace datetime.now() with timezone.now()
        feed = feedparser.parse(feed_url)
        new_links = []

        for entry in feed.entries:
            if hasattr(entry, 'published_parsed'):
                published_date = timezone.make_aware(datetime(*entry.published_parsed[:6]))
                if published_date > last_fetched:
                    new_links.append((entry.link, published_date))

        for link, pub_date in new_links:
            try:
                article = Article(link)
                article.download()
                article.parse()
                article.nlp()

                slug = slugify(article.title)
                if NewsArticle.objects.filter(slug=slug).exists():
                    continue

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
                    published_date=timezone.localtime(pub_date),
                    image_url=image_list[0] if len(image_list) > 0 else '',
                    image_url_2=image_list[1] if len(image_list) > 1 else '',
                    image_url_3=image_list[2] if len(image_list) > 2 else '',
                    slug=slug
                )
            except Exception as err:
                logging.warning(f"Failed to fetch article from {link}: {err}")

        category.last_fetched = timezone.now()  # Use timezone.now() here as well
        category.save()

        logging.info(f"Fetched {len(new_links)} new articles for '{category_name}'")

    except Exception as e:
        logging.error(f"Error fetching articles for {category_name}: {e}")
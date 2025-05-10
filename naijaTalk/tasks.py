# /naijaTalk/tasks.py

from celery import shared_task
from newspaper import Article, build
from naijaTalk.models import NewsArticle, NewsCategory
from django.utils.text import slugify
from django.utils import timezone

@shared_task
def fetch_all_news():
    sources = [
        ("Sport", "https://www.espn.com"),
        ("Entertainment", "https://www.eonline.com"),
        ("Entertainment", "https://www.pulse.ng/entertainment"),
        ("Education", "https://www.edutopia.org"),
        ("Health Care", "https://www.medicalnewstoday.com"),
        ("Finance", "https://www.investopedia.com"),
        ("Business", "https://www.businessinsider.com"),
        ("Celebrity", "https://www.tmz.com"),
        ("Celebrity", "https://www.lindaikejisblog.com"),
        ("Technology", "https://techcrunch.com"),
        ("Local News", "https://punchng.com"),
        ("Politics", "https://www.politico.com"),
        ("Science", "https://www.sciencenews.org"),
        ("World News", "https://www.aljazeera.com/news")
]

    for category_name, source_url in sources:
        try:
            # Use Newspaper3k's `build` to extract articles from a source
            paper = build(source_url, memoize_articles=False)

            category, _ = NewsCategory.objects.get_or_create(
                name=category_name,
                defaults={"slug": slugify(category_name)}
            )

            for content in paper.articles[:5]:  # Limit to 5 articles per source
                try:
                    content.download()
                    content.parse()
                    content.nlp()

                    slug = slugify(content.title)

                    if NewsArticle.objects.filter(slug=slug).exists():
                        continue  # Avoid duplicates

                    images = content.images if content.images else []
                    image_list = list(images)[:3]
                    while len(image_list) < 3:
                        image_list.append(image_list[-1] if image_list else '')

                    video_url = content.movies[0] if content.movies else None

                    NewsArticle.objects.create(
                    title=content.title,
                    summary=content.summary,
                    content=content.text,
                    author=", ".join(content.authors) if content.authors else "Anonymous",
                    category=category,
                    published_date=content.publish_date if content.publish_date else timezone.now(),
                    image_url=image_list[0] if len(image_list) > 0 else '',
                    image_url_2=image_list[1] if len(image_list) > 1 else '',
                    image_url_3=image_list[2] if len(image_list) > 2 else '',
                    video_url=video_url,
                    slug=slug
                )
                except Exception as e:
                    print(f"Error processing article from {source_url}: {e}")

        except Exception as e:
            print(f"Error fetching from source {source_url}: {e}")
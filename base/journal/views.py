import os
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from .models import Article


def home(request):
    """Главная страница портала"""
    return render(request, "journal/home.html")


def journal_home(request):
    """Страница со списком статей"""
    articles = Article.objects.filter(is_published=True).order_by("-published_at", "-created_at")
    return render(request, "journal/journal_home.html", {"articles": articles})


def article_detail(request, slug):
    """Страница конкретной статьи"""
    article = get_object_or_404(Article, slug=slug, is_published=True)

    if article.has_archive():
        index_path = os.path.join(settings.MEDIA_ROOT, "articles", article.slug, "index.html")
        if os.path.exists(index_path):
            with open(index_path, encoding="utf-8") as f:
                html_content = f.read()
            return render(
                request,
                "journal/article_from_zip.html",
                {"article": article, "html_content": html_content}
            )

    return render(request, "journal/article_detail.html", {"article": article})

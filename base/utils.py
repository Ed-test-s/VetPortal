from django.utils.text import slugify
from django.db import IntegrityError
import itertools


def generate_unique_slug(model_instance, slug_field_name, slug_from_field):
    """
    Генерация уникального slug для модели.
    model_instance — объект модели
    slug_field_name — имя поля slug в модели (строка)
    slug_from_field — имя поля, откуда берём текст (строка)
    """
    slug = slugify(getattr(model_instance, slug_from_field))
    ModelClass = model_instance.__class__
    unique_slug = slug
    for i in itertools.count(1):
        if not ModelClass.objects.filter(**{slug_field_name: unique_slug}).exclude(pk=model_instance.pk).exists():
            break
        unique_slug = f"{slug}-{i}"
    return unique_slug

from django.contrib import admin
from .models import Review
from django.contrib.contenttypes.models import ContentType


class ContentTypeFilter(admin.SimpleListFilter):
    title = "Тип объекта"
    parameter_name = "content_type"

    def lookups(self, request, model_admin):
        # показываем только нужные модели
        allowed = ContentType.objects.filter(
            model__in=["clinicservice", "groomingservice", "medicine"]
        )
        return [(ct.id, ct.model_class().__name__) for ct in allowed]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(content_type_id=self.value())
        return queryset


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "text", "rating", "target_object", "created_at")
    search_fields = ("text", "user__username")
    list_filter = (ContentTypeFilter,)  # фильтр

    def target_object(self, obj):
        return str(obj.content_object)
    target_object.short_description = "Объект"

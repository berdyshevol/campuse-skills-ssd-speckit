from django.contrib import admin

from .models import BookingRequest, Category, Review, Skill


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ("is_active",)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "owner",
        "category",
        "is_free",
        "price",
        "availability",
        "created_at",
    )
    list_filter = ("category", "availability", "is_free")
    search_fields = ("title", "description")
    raw_id_fields = ("owner",)


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ("skill", "requester", "status", "created_at")
    list_filter = ("status",)
    raw_id_fields = ("skill", "requester")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("skill", "author", "rating", "created_at")
    list_filter = ("rating",)
    raw_id_fields = ("skill", "author")

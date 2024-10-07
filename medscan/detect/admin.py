from django.contrib import admin

from .models import Job, ModelVersion, TestKit, TestKitGroup


@admin.register(ModelVersion)
class ModelVersionAdmin(admin.ModelAdmin):
    list_display = ("id", "model", "version", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("id", "model__name", "description")
    readonly_fields = ("version", "local_model_path")
    fieldsets = (
        (
            None,
            {"fields": ("model", "description", "class_to_label", "local_model_path", "version")},
        ),
        ("Status", {"fields": ("is_active",)}),
    )

    def save_model(self, request, obj, form, change):
        if obj.is_active:
            obj.load_model()
        super().save_model(request, obj, form, change)


@admin.register(TestKitGroup)
class TestKitGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "uid", "created_at", "updated_at")
    search_fields = (
        "id",
        "uid",
    )
    fieldsets = (
        (None, {"fields": ("uid",)}),
        (
            "Dynamic Configuration",
            {
                "fields": (
                    "class_to_label",
                    "activation_alias",
                )
            },
        ),
        (
            "Combo Kit Configuration",
            {
                "fields": (
                    "child_sequence",
                    "parent_kit",
                )
            },
        ),
    )


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("id", "image", "status", "model_version", "created_at")
    list_filter = ("status", "model_version")
    search_fields = ("id", "image__id", "model_version__id")
    readonly_fields = ("result", "error")
    fieldsets = (
        (None, {"fields": ("image", "model_version", "test_kit_group")}),
        ("Status", {"fields": ("status",)}),
        ("Result", {"fields": ("result", "error")}),
    )


@admin.register(TestKit)
class TestKitAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "score", "job", "is_ok", "created_at")
    list_filter = ("job__model_version", "is_ok")
    search_fields = ("id", "name", "job__id")
    readonly_fields = ("box", "name", "score", "job")
    fieldsets = (
        (None, {"fields": ("name", "score", "box", "job")}),
        ("Feedback", {"fields": ("is_ok", "feedback_label")}),
    )

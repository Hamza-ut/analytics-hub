from django.contrib import admin
from .models import File


# To register the File model with the admin site and customize its display
class FileAdmin(admin.ModelAdmin):
    list_display = (
        "upload_id",
        "user",
        "original_filename",
        "file_size",
        "status",
        "uploaded_at",
    )
    search_fields = ("upload_id", "original_filename", "user__username")
    list_filter = ("status", "uploaded_at")

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            if obj.timepoint_runs.exists():
                self.message_user(
                    request,
                    f"Cannot delete '{obj.original_filename}': it is used by a project.",
                    level="error",
                )
                return
        queryset.delete()



admin.site.register(File, FileAdmin)

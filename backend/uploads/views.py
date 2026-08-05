import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from uploads.models import File
from .utils import allowed_extension_and_size_check


from .tasks import process_file_pipeline_task


@login_required
def upload_view(request):
    if request.method == "POST":
        uploaded_file = request.FILES["file"]

        # 1. Keep the quick validation (Checks format and size bounds instantly)
        is_valid, error_msg = allowed_extension_and_size_check(uploaded_file)
        if not is_valid:
            return render(request, "uploads/upload.html", {"error": error_msg})

        # 2. Let Django write the file to the local media staging directory.
        # NOTICE: We do NOT calculate MD5 here. Status defaults to "UPLOADING".
        file_record = File.objects.create(
            user=request.user,
            file=uploaded_file,
            original_filename=uploaded_file.name,
            file_size=uploaded_file.size,
            status="UPLOADING",  # Let the dashboard know it's processing in the background!
        )

        # 3. TRIGGER CELERY BACKGROUND WORKER
        # This sends a tiny notification packet to your message broker (Redis/RabbitMQ).
        # It takes about 2 milliseconds to hand over, and then the view moves on!
        process_file_pipeline_task.delay(file_record.id)

        # 4. INSTANT REDIRECT
        # The user gets sent to the dashboard immediately. No browser spin or timeouts!
        return redirect("dashboard:dashboard")

    return render(request, "uploads/upload.html")

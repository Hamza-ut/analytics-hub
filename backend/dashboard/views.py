# dashboard/views.py

from uploads.models import File
from django.contrib import messages
from projects.utils import is_stuck
from projects.models import ProjectRun
from django.db.models import Sum, Count
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.http import Http404, FileResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.postgres.aggregates import StringAgg
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect


@require_POST
@login_required
def delete_project_view(request, project_id):
    # 1. Fetch project
    project = get_object_or_404(ProjectRun, id=project_id)

    # 2. Permission Check: Only admin can delete (or owner, if you choose)
    if not request.user.is_superuser and project.user != request.user:
        raise Http404("You do not have permission to delete this project.")

    # 3. Prevent deleting while it's actually running
    if project.status == "RUNNING" and not is_stuck(project):
        messages.error(request, "Cannot delete a project while it is running.")
        return redirect("dashboard:dashboard")

    # 4. Cleanup
    project_name = project.project_id
    project.delete()  # This also deletes TimepointResult due to CASCADE
    
    messages.success(request, f"Project {project_name} has been deleted.")
    return redirect("dashboard:dashboard")


@require_POST
@login_required
def delete_file_view(request, file_id):
    # Step 1: fetch the file object
    file_obj = get_object_or_404(File, id=file_id)
    # Step 2: check permissions
    if file_obj.user != request.user and not request.user.is_superuser:
        # the user is neither the owner nor admin → deny
        raise Http404("You do not have permission to delete this file.")

    # Step 3: check if any projects are using this file
    if file_obj.projects.exists():
        # Add an error message
        messages.error(
            request,
            f"Cannot delete '{file_obj.original_filename}': It is being used by one or more projects.",
        )
        return redirect("dashboard:dashboard")
    # Step 4: delete the file (this triggers post_delete signal)
    file_obj.delete()
    # Step 5: redirect to dashboard with a success message
    return redirect("dashboard:dashboard")


@login_required
def download_file_view(request, file_id):
    # Step 1: fetch file object
    file_obj = get_object_or_404(File, id=file_id)

    # Step 2: permission check
    if file_obj.user != request.user and not request.user.is_superuser:
        raise Http404("You do not have permission to download this file.")

    # Step 3: send file as a response
    if not file_obj.file:
        raise Http404("File not found on the server.")

    response = FileResponse(file_obj.file.open("rb"), as_attachment=True)
    response["Content-Disposition"] = (
        f'attachment; filename="{file_obj.original_filename}"'
    )
    return response


@login_required
def dashboard_view(request):
    # 1. Fetch Projects & Files based on user role
    if request.user.is_superuser:
        files = File.objects.all()
        projects = ProjectRun.objects.all().prefetch_related("files")
    else:
        files = File.objects.filter(user=request.user)
        projects = ProjectRun.objects.filter(user=request.user).prefetch_related("files")

    # 2. Get file names for project display
    projects = ProjectRun.objects.annotate(
        file_names=StringAgg('files__original_filename', delimiter=', ')
    )
    # 3. Identify "Locked" files (those associated with any project)
    # values_list returns a list of IDs; we turn it into a set for O(1) lookup speed
    locked_file_ids = set(
        ProjectRun.objects.values_list('files', flat=True)
    )

    # 4. Filter Uploads (Search)
    search_query = request.GET.get("search")
    if search_query:
        files = files.filter(original_filename__icontains=search_query)

    # 5. Sort Uploads
    allowed_sorts = ["upload_id", "-upload_id", "uploaded_at", "-uploaded_at", 
                     "file_size", "-file_size", "original_filename", "-original_filename"]
    sort = request.GET.get("sort", "-uploaded_at")
    if sort not in allowed_sorts:
        sort = "-uploaded_at"
    files = files.order_by(sort)

    # 6. Stats & Pagination
    stats = files.aggregate(total_files=Count("id"), total_size=Sum("file_size"))
    file_paginator = Paginator(files, 5)
    file_page_number = request.GET.get("page", 1)
    files_obj = file_paginator.get_page(file_page_number)

    return render(
        request,
        "dashboard/dashboard.html",
        {
            "projects": projects,
            "files": files_obj,
            "locked_file_ids": locked_file_ids,
            "total_files": stats["total_files"],
            "total_size": stats["total_size"] or 0,
            "search_query": search_query,
            "sort": sort,
        },
    )
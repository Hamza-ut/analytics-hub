from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm


# render always take template path
def home_view(request):
    return render(request, "index.html")


# redirect always take url name
def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            username = user.username  
            messages.success(request, f"Account created for {username}!")
            return redirect("dashboard:dashboard")
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/signup.html", {"form": form})


def login_view(request):
    # Redirect authenticated users immediately
    if request.user.is_authenticated:
        return redirect("dashboard:dashboard")  # or "home" if you prefer

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard:dashboard")
    else:
        form = AuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("accounts:login")



#####################################################################################################################
# def test_view(request):
#     if request.method == "POST":
#         username = request.POST.get("username")  # string
#         password = request.POST.get("password")  # string
#         return HttpResponse(f"Username: {username}, Password: {password}")
#     else:
#         name = request.GET.get("name", "Default-Admin")
#         return render(request, "template.html", {"name": name})


# from django.http import HttpResponse
# from django.shortcuts import render
# from django.http import JsonResponse
# from django.http import FileResponse

# def test_view(request):
#     # request.method can be 'GET' or 'POST'
#     name = request.GET.get("name", "Guest")
#     second = int(request.GET.get("age", 20))
#     return HttpResponse(f"Hello, {name}, your age is {second}!")

# def test_view(request):
#     name = request.GET.get("name","Default-Admin")
#     return render(request, "template.html", {"name": name})


# def test_view(request):
#     return JsonResponse({"status": "ok", "user": "Hamza"})

# def test_view(request):
#     f = open("myfile.pdf", "rb")  # keep it open
#     return FileResponse(f)


# return HttpResponse(...)
# return render(...)
# return redirect(...)
# return JsonResponse(...)
# return HttpResponseRedirect(...)
# return FileResponse(...)


# request.user.is_authenticated
# request.user.username
# request.user.email
# request.user.is_staff
# request.user.is_superuser


# @login_required
# @require_POST
# @permission_required


# user = User(username="alice", email="alice@example.com")
# user.save()

from django.shortcuts import render


def home(request):
    return render(request, "/student_portal/home.html")

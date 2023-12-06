from django.shortcuts import render


def home(request):
    return render(request, "portals/Faculty_Profile.html")

from django.shortcuts import render


def studenthome(request):
    return render(request, "student_portal/studenthome.html")

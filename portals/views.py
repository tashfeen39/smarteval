from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages



def home(request):
    return render(request, "portals/Faculty_Profile.html")

def faculty_class_info_view(request):
    return render(request, "portals/Faculty_ClassInfo.html")

def faculty_complaints_view(request):
    return render(request, "portals/Faculty_Complaints.html")

def faculty_dashboard_view(request):
    return render(request, "portals/Faculty_Dashboard.html")

def faculty_display_classes_view(request):
    return render(request, "portals/Faculty_DisplayClasses.html")    

def faculty_feedback_view(request):
    return render(request, "portals/Faculty_Feedbacks.html")

def faculty_generate_exam_view(request):
    return render(request, "portals/Faculty_GenerateExam.html")

def faculty_grading_view(request):
    return render(request, "portals/Faculty_Grading.html")

def faculty_marks_entry_view(request):
    return render(request, "portals/Faculty_MarksEntry.html")

def faculty_profile_view(request):
    return render(request, "portals/Faculty_Profile.html")

def faculty_student_info_view(request):
    return render(request, "portals/Faculty_StudentInfo.html")

def faculty_student_marks_entry_view(request):
    return render(request, "portals/Faculty_StudentsMarksEntry.html")

def faculty_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        print(f"Attempting login for username: {username}")

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_teacher:
            login(request, user)
            messages.success(request, 'Login successful!')
            print(f"Login successful for user: {username}")
            return redirect('portals:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
            print(f"Login failed for user: {username}")

    return render(request, 'portals/faculty_login.html')
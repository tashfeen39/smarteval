from django.shortcuts import render


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

def student_dashboard_view(request):
    return render(request, "portals/Student_Dashboard.html")

def student_registeredcourses_view(request):
    return render(request, "portals/Student_RegisteredCourses.html")
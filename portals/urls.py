from django.urls import path
from . import views

app_name = 'portals'
urlpatterns = [
    path("", views.home, name="home"),
    path("faculty/", views.faculty_dashboard_view, name="dashboard"),
    path("faculty/class-info/", views.faculty_class_info_view, name="class-info"),
    path("faculty/complaints/", views.faculty_complaints_view, name="complaints"),
    path("faculty/display-classes/", views.faculty_display_classes_view, name="display-classes"),
    path("faculty/feedbacks/", views.faculty_feedback_view, name="feedbacks"),
    path("faculty/generate-exam/", views.faculty_generate_exam_view, name="generate-exam"),
    path("faculty/grading/", views.faculty_grading_view, name="grading"),
    path("faculty/enter-marks/", views.faculty_marks_entry_view, name="ter-marks"),
    path("faculty/my-profile/", views.faculty_profile_view, name="my-profile"),
    path("faculty/student-info/", views.faculty_student_info_view, name="student-info"),
]

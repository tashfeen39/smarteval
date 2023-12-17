from django.urls import path
from . import views

app_name = 'portals'
urlpatterns = [
    path("", views.home, name="home"),
    path("faculty/dashboard/", views.faculty_dashboard_view, name="dashboard"),
    path("faculty/class-info/", views.faculty_class_info_view, name="class-info"),
    path("faculty/complaints/", views.faculty_complaints_view, name="complaints"),
    path("faculty/display-classes/", views.faculty_display_classes_view, name="display-classes"),
    path("faculty/feedbacks/", views.faculty_feedback_view, name="feedbacks"),
    path("faculty/generate-exam/", views.faculty_generate_exam_view, name="generate-exam"),
    path("faculty/grading/", views.faculty_grading_view, name="grading"),
    path("faculty/enter-marks/", views.faculty_marks_entry_view, name="enter-marks"),
    path("faculty/my-profile/", views.faculty_profile_view, name="my-profile"),
    path("faculty/student-info/", views.faculty_student_info_view, name="student-info"),
    path("faculty/student-marksentry/", views.faculty_student_marks_entry_view, name="student-marksentry"),
    path("student/dashboard/", views.student_dashboard_view, name="student-dashboard"),
    path("student/RegisteredCourses/", views.student_registeredcourses_view, name="student-registeredcourses"),
    path("student/timetable/", views.student_timetable_view, name="student-timetable"),
    path("student/report/", views.student_report_view, name="student-report"),
    path("student/feedback/", views.student_feedback_view, name="student-feedback"),
    path("student/complaint/", views.student_complaint_view, name="student-complaint"),


]

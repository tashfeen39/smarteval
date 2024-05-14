from django.urls import path
from . import views
from .views import generate_paper


app_name = 'portals'
urlpatterns = [
    path("", views.faculty_profile_view, name="my-profile"),
    path("faculty/login/", views.faculty_login_view, name="faculty-login"),
    path("faculty/dashboard/", views.faculty_dashboard_view, name="dashboard"),
    path('class-info/<int:sectioncourse_pk>/', views.faculty_class_info_view, name='class-info'),
    path("faculty/display-classes/", views.faculty_display_classes_view, name="display-classes"),
    path("faculty/feedbacks/", views.faculty_feedback_view, name="feedbacks"),
    path("faculty/generate-exam/", views.faculty_generate_exam_view, name="generate-exam"),
    path("update-class-taken/", views.update_class_taken, name='update_class_taken'),
    path('find-available-time-slots/', views.find_available_time_slots, name='find_available_time_slots'),
    # For generating the paper
    path("generate_paper/", views.generate_paper, name="generate_paper"),
    path("regenerate_question/", views.regenerate_question, name="regenerate_question"),
    path("faculty/grading/", views.faculty_grading_view, name="grading"),
    path("faculty/studentsreports/", views.faculty_studentsreports_view, name="studentsreports"),
    path("faculty/enter-marks/", views.faculty_marks_entry_view, name="enter-marks"),
    path("faculty/my-profile/", views.faculty_profile_view, name="my-profile"),
    path('faculty/student-info/<str:student_id>/<str:teachersectioncourse_id>/', views.faculty_student_info_view, name='student-info'),
    path('faculty/student-marks-entry/<str:teachersectioncourse_id>/', views.faculty_student_marks_entry_view, name='student-marksentry'),
    path('faculty/save-marks/<int:teachersectioncourse_id>/', views.faculty_save_marks_view, name='save-marks'),
    path("faculty/registration/", views.faculty_registration, name="faculty-registration"),
    path("student/login/", views.student_login_view, name="student-login"),
    path("student/dashboard/", views.student_dashboard_view, name="student-dashboard"),
    path("student/RegisteredCourses/", views.student_registeredcourses_view, name="student-registeredcourses"),
    path("student/timetable/", views.student_timetable_view, name="student-timetable"),
    path("student/report/", views.student_report_view, name="student-report"),
    path("student/feedback/", views.student_feedback_view, name="student-feedback"),
    path("student/profile/", views.student_profile_view, name="student-profile"),
    path("student/subjectwisereport/", views.student_subjectwisereport_view, name="student-subjectwisereport"),
    path("student/registration/", views.student_registration, name="student-registration"),
    path('get_programs/', views.get_programs, name='get_programs'),
    path("logout/", views.log_out, name="logout"),


]

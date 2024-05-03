from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin import RelatedFieldListFilter
from portals.forms import DegreeForm
from .models import Course, CoursePrerequisite, Degree, Department, Program, School, SemesterCourses, SemesterDetails, TeacherCoursesTaught, User, Student, Teacher, SemesterDetails, Section


class StudentAdmin(admin.ModelAdmin):
    # list_display = ['user', 'StudentID', 'date_of_birth', 'gender', 'marital_status', 'religion', 'nationality', 'cnic', 'father_name', 'father_occupation', 'semester', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'StudentID']
    list_filter = ('user__is_student', 'user__is_teacher', 'degree', 'semester', 'section__section_name')
    readonly_fields = ('StudentID',)

class TeacherAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    list_filter = ('user__is_student', 'user__is_teacher', 'department')
    

class TeacherCoursesTaughtAdmin(admin.ModelAdmin):
    pass


class SectionAdmin(admin.ModelAdmin):
    search_fields = ('semester', 'section_name')
    list_filter = ('semester', 'section_name', 'degree')


class CustomUserAdmin(admin.ModelAdmin):
    # list_display = ('username', 'email', 'first_name', 'last_name', 'is_student', 'is_teacher', 'phone_number', 'profile_picture')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    list_filter = ('is_staff', 'is_superuser', 'is_student', 'is_teacher')


class CustomAdminSite(admin.AdminSite):
    site_header = "SMARTEVAL ADMINISTRATION"


class SchoolAdmin(admin.ModelAdmin):
    search_fields = ('school_name',)


class DepartmentAdmin(admin.ModelAdmin):
    search_fields = ('department_name',)
    list_filter = ('school',)

class ProgramAdmin(admin.ModelAdmin):
    list_filter = ('department',)
   

@admin.register(Degree)
class DegreeAdmin(admin.ModelAdmin):
    form = DegreeForm
    search_fields = ('degree_name',)
    list_filter = ('department',)


class SemesterDetailsAdmin(admin.ModelAdmin):
    list_filter = ('degree__department',)



class CourseAdmin(admin.ModelAdmin):
    search_fields = ['course_name']
    list_filter = ('department',)


class SemesterCoursesAdmin(admin.ModelAdmin):
    search_fields = ['courses__course_name']
    list_filter = ('semester_details__semester_number','semester_details__degree__department')

class CoursePrerequisiteAdmin(admin.ModelAdmin):
    pass


custom_admin_site = CustomAdminSite()
admin.site = custom_admin_site



admin.site.register(User, CustomUserAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Program, ProgramAdmin)
admin.site.register(Degree, DegreeAdmin)
admin.site.register(SemesterDetails, SemesterDetailsAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(SemesterCourses, SemesterCoursesAdmin)
admin.site.register(CoursePrerequisite, CoursePrerequisiteAdmin)
admin.site.register(TeacherCoursesTaught, TeacherCoursesTaughtAdmin)
admin.site.register(Section, SectionAdmin)

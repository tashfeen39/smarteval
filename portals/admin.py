from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin import RelatedFieldListFilter
from portals.forms import DegreeForm
from .models import Course, CoursePrerequisite, Degree, Department, Program, School, SemesterCourses, SemesterDetails, TeacherCoursesTaught, User, Student, Teacher, SemesterDetails


class StudentAdmin(admin.ModelAdmin):
    # list_display = ['user', 'StudentID', 'date_of_birth', 'gender', 'marital_status', 'religion', 'nationality', 'cnic', 'father_name', 'father_occupation', 'semester', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'StudentID']
    list_filter = ('user__is_student', 'user__is_teacher', 'degree')
    readonly_fields = ('StudentID',)

class TeacherAdmin(admin.ModelAdmin):
    list_filter = ('user__is_student', 'user__is_teacher', 'department')
    

class TeacherCoursesTaughtAdmin(admin.ModelAdmin):
    pass


class CustomUserAdmin(admin.ModelAdmin):
    # list_display = ('username', 'email', 'first_name', 'last_name', 'is_student', 'is_teacher', 'phone_number', 'profile_picture')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_student', 'is_teacher')


class CustomAdminSite(admin.AdminSite):
    site_header = "SMARTEVAL ADMINISTRATION"


class SchoolAdmin(admin.ModelAdmin):
    pass

class DepartmentAdmin(admin.ModelAdmin):
    list_filter = ('school',)

class ProgramAdmin(admin.ModelAdmin):
    list_filter = ('department',)
   

@admin.register(Degree)
class DegreeAdmin(admin.ModelAdmin):
    form = DegreeForm
    list_filter = ('department',)


# class DepartmentFilter(admin.RelatedFieldListFilter):
#     def field_choices(self, field, request, model_admin):
#         # Get all unique departments associated with degrees that have semester details
#         queryset = field.related_model.objects.filter(degree__isnull=False).distinct()
#         print(queryset)
#         departments = set([str(department) for department in queryset])

#         return [(department, department) for department in departments]

        


class SemesterDetailsAdmin(admin.ModelAdmin):
    # list_filter = (('degree__department', DepartmentFilter),)
      list_filter = ('degree__department',)



class CourseAdmin(admin.ModelAdmin):
    search_fields = ['course_name']
    list_filter = ('department',)


class SemesterCoursesAdmin(admin.ModelAdmin):
    pass

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

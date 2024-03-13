from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.admin import UserAdmin
from .models import User, Student, Teacher

# class UserAdmin(admin.ModelAdmin):
#     pass

class StudentAdmin(admin.ModelAdmin):
    # list_display = ['user', 'StudentID', 'date_of_birth', 'gender', 'marital_status', 'religion', 'nationality', 'cnic', 'father_name', 'father_occupation', 'semester', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'StudentID']
    readonly_fields = ('StudentID',)

class TeacherAdmin(admin.ModelAdmin):
    pass


# # Custom User Admin Form
# class CustomUserCreationForm(UserCreationForm):
#     class Meta:
#         model = User
#         fields = ('username', 'email', 'is_student', 'is_teacher')

# class CustomUserChangeForm(UserChangeForm):
#     class Meta:
#         model = User
#         fields = ('username', 'email', 'is_student', 'is_teacher')

# Custom User Admin
class CustomUserAdmin(UserAdmin):
    # form = CustomUserChangeForm
    # add_form = CustomUserCreationForm

    # fieldsets = UserAdmin.fieldsets + (
    #     (None, {'fields': ('is_student', 'is_teacher')}),
    # )

    # list_display = ('username', 'email', 'is_student', 'is_teacher')
    pass

class CustomAdminSite(admin.AdminSite):
    site_header = "SMARTEVAL ADMINISTRATION"


custom_admin_site = CustomAdminSite()
admin.site = custom_admin_site



admin.site.register(User, CustomUserAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)

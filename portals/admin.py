from django.contrib import admin
from .models import User, Student, Teacher

class UserAdmin(admin.ModelAdmin):
    pass

class StudentAdmin(admin.ModelAdmin):
    pass

class TeacherAdmin(admin.ModelAdmin):
    pass


class CustomAdminSite(admin.AdminSite):
    site_header = "SMARTEVAL ADMINISTRATION"


custom_admin_site = CustomAdminSite()
admin.site = custom_admin_site



admin.site.register(User, UserAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'get_full_name_display', 'user_type', 'get_stats', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('user_type', 'is_staff', 'is_active', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)
    list_per_page = 25
    
    fieldsets = UserAdmin.fieldsets + (
        ('User Type', {'fields': ('user_type',)}),
        ('Profile', {'fields': ('profile_picture', 'phone', 'bio', 'date_of_birth')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type', 'first_name', 'last_name'),
        }),
    )
    
    def get_full_name_display(self, obj):
        return obj.get_full_name() or '-'
    get_full_name_display.short_description = 'Full Name'
    
    def get_stats(self, obj):
        if obj.user_type == 'instructor':
            courses = obj.courses_taught.count()
            students = obj.courses_taught.aggregate(
                total=Count('enrollments', distinct=True)
            )['total'] or 0
            return format_html(
                '<span style="color: blue;">📚 {} courses | 👥 {} students</span>',
                courses, students
            )
        elif obj.user_type == 'student':
            enrollments = obj.enrollments.filter(is_active=True).count()
            completed = obj.enrollments.filter(completed=True).count()
            return format_html(
                '<span style="color: green;">📖 {} enrolled | ✅ {} completed</span>',
                enrollments, completed
            )
        return '-'
    get_stats.short_description = 'Statistics'
    

    actions = ['make_instructor', 'make_student', 'make_admin', 'activate_users', 'deactivate_users']
    
    def make_instructor(self, request, queryset):
        count = queryset.update(user_type='instructor')
        self.message_user(request, f'{count} users changed to Instructor.')
    make_instructor.short_description = 'Change role to Instructor'
    
    def make_student(self, request, queryset):
        count = queryset.update(user_type='student')
        self.message_user(request, f'{count} users changed to Student.')
    make_student.short_description = 'Change role to Student'
    
    def make_admin(self, request, queryset):
        count = queryset.update(user_type='admin', is_staff=True)
        self.message_user(request, f'{count} users changed to Admin.')
    make_admin.short_description = 'Change role to Admin'
    
    def activate_users(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} users activated.')
    activate_users.short_description = 'Activate selected users'
    
    def deactivate_users(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} users deactivated.')
    deactivate_users.short_description = 'Deactivate selected users'

admin.site.register(User, CustomUserAdmin)

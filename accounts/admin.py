from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, RegistrationRequest
from django.utils.html import format_html
from django.conf import settings
from django.core.mail import send_mail
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

@admin.register(RegistrationRequest)
class RegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'status', 'submitted_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('name', 'email', 'phone')
    ordering = ('-submitted_at',)
    readonly_fields = ('submitted_at',)
    actions = ['mark_processed', 'mark_rejected']

    def _send_registration_email(self, obj):
        registration_url = f"{settings.SITE_URL}/accounts/register/"
        subject = 'Registration Approved - Complete Your LMS Registration'
        message = f'''Dear {obj.name},

Your registration request has been approved.

Please complete your registration using the link below:
{registration_url}

Best regards,
LMS Team
'''

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [obj.email],
            fail_silently=False,
        )

    def mark_processed(self, request, queryset):
        updated = 0
        emailed = 0
        for obj in queryset:
            obj.status = 'processed'
            if not obj.email_sent:
                self._send_registration_email(obj)
                obj.email_sent = True
                emailed += 1
            obj.save(update_fields=['status', 'email_sent'])
            updated += 1
        self.message_user(request, f"{updated} registration request(s) marked processed. Registration email sent to {emailed} user(s).")
    mark_processed.short_description = 'Mark selected registration requests as processed'

    def mark_rejected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f"{updated} registration request(s) marked rejected.")
    mark_rejected.short_description = 'Mark selected registration requests as rejected'


admin.site.register(User, CustomUserAdmin)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.http import HttpResponse
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html
from openpyxl import Workbook
from openpyxl.styles import Font

from .models import User, RegistrationRequest

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
    change_list_template = 'admin/accounts/registrationrequest/change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'export/',
                self.admin_site.admin_view(self.export_registration_requests),
                name='accounts_registrationrequest_export',
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        export_url = reverse('admin:accounts_registrationrequest_export')
        query_string = request.GET.urlencode()
        extra_context['export_url'] = f'{export_url}?{query_string}' if query_string else export_url
        return super().changelist_view(request, extra_context=extra_context)

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

    def export_registration_requests(self, request):
        changelist = self.get_changelist_instance(request)
        queryset = changelist.get_queryset(request)

        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = 'Registration Requests'

        headers = ['ID', 'Name', 'Email', 'Phone', 'Status', 'Submitted At']
        worksheet.append(headers)

        for cell in worksheet[1]:
            cell.font = Font(bold=True)

        for registration_request in queryset:
            submitted_at = registration_request.submitted_at
            if timezone.is_aware(submitted_at):
                submitted_at = timezone.localtime(submitted_at)

            worksheet.append([
                registration_request.id,
                registration_request.name,
                registration_request.email,
                registration_request.phone,
                registration_request.get_status_display(),
                submitted_at.strftime('%Y-%m-%d %H:%M:%S') if submitted_at else '',
            ])

        for column_cells in worksheet.columns:
            max_length = max(len(str(cell.value or '')) for cell in column_cells)
            worksheet.column_dimensions[column_cells[0].column_letter].width = min(max_length + 2, 40)

        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = (
            f'attachment; filename="registration_requests_{timestamp}.xlsx"'
        )
        workbook.save(response)
        return response


admin.site.register(User, CustomUserAdmin)

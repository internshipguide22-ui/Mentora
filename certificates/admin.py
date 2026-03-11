from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Certificate

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('get_student', 'get_course', 'issued_date', 'certificate_id')
    list_filter = ('issued_date',)
    search_fields = ('enrollment__student__username', 'enrollment__course__title', 'uuid')
    date_hierarchy = 'issued_date'
    readonly_fields = ('uuid', 'issued_date')
    list_per_page = 25
    
    fieldsets = (
        ('Certificate Info', {
            'fields': ('enrollment', 'uuid', 'issued_date')
        }),
        ('File', {
            'fields': ('file',)
        }),
    )
    
    actions = ['revoke_certificates', 'regenerate_certificates']
    
    def get_student(self, obj):
        return obj.enrollment.student.get_full_name() or obj.enrollment.student.username
    get_student.short_description = 'Student'
    
    def get_course(self, obj):
        return obj.enrollment.course.title
    get_course.short_description = 'Course'
    
    def certificate_id(self, obj):
        return format_html('<code>{}</code>', str(obj.uuid)[:8])
    certificate_id.short_description = 'ID'
    

    def revoke_certificates(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count} certificates revoked.')
    revoke_certificates.short_description = 'Revoke selected certificates'
    
    def regenerate_certificates(self, request, queryset):
        from .utils import generate_certificate_pdf
        count = 0
        for cert in queryset:
            generate_certificate_pdf(cert)
            count += 1
        self.message_user(request, f'{count} certificates regenerated.')
    regenerate_certificates.short_description = 'Regenerate certificates'

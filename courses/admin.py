from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Course, Enrollment, Module, Lesson, Category, CourseNote

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'course_count')
    search_fields = ('name',)
    
    def course_count(self, obj):
        return obj.courses.count()
    course_count.short_description = 'Courses'

class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    fields = ('title', 'description', 'order')

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ('title', 'description', 'order')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'enrollment_count', 'module_count', 'lesson_count', 'completion_rate', 'created_at')
    list_filter = ('category', 'instructor', 'created_at')
    search_fields = ('title', 'description', 'instructor__username')
    date_hierarchy = 'created_at'
    inlines = [ModuleInline]
    readonly_fields = ('created_at', 'updated_at', 'get_student_list', 'get_course_statistics')
    list_per_page = 20
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'instructor', 'category')
        }),
        ('Media', {
            'fields': ('thumbnail', 'syllabus')
        }),
        ('Statistics', {
            'fields': ('get_course_statistics',),
            'classes': ('wide',)
        }),
        ('Enrolled Students', {
            'fields': ('get_student_list',),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['assign_to_instructor', 'delete_courses']
    
    def enrollment_count(self, obj):
        count = obj.enrollments.count()
        return format_html('<span style="color: green; font-weight: bold;">{}</span>', count)
    enrollment_count.short_description = 'Enrollments'
    
    def module_count(self, obj):
        return obj.modules.count()
    module_count.short_description = 'Modules'
    
    def lesson_count(self, obj):
        return sum(module.lessons.count() for module in obj.modules.all())
    lesson_count.short_description = 'Lessons'
    
    def completion_rate(self, obj):
        total = obj.enrollments.filter(is_active=True).count()
        if total == 0:
            return '-'
        completed = obj.enrollments.filter(completed=True).count()
        rate = (completed / total * 100)
        color = 'green' if rate >= 50 else 'orange' if rate >= 25 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.0f}%</span>',
            color, rate
        )
    completion_rate.short_description = 'Completion Rate'
    
    def get_course_statistics(self, obj):
        total_enrollments = obj.enrollments.filter(is_active=True).count()
        completed_enrollments = obj.enrollments.filter(completed=True).count()
        active_students = obj.enrollments.filter(is_active=True, completed=False).count()
        total_modules = obj.modules.count()
        total_lessons = sum(module.lessons.count() for module in obj.modules.all())
        
        html = '<div style="padding: 15px; background: #f0f8ff; border-radius: 5px;">'
        html += f'<h3 style="margin-top: 0;">Course Statistics</h3>'
        html += f'<table style="width: 100%; border-collapse: collapse;">'
        html += f'<tr><td style="padding: 5px;"><strong>Total Enrollments:</strong></td><td>{total_enrollments}</td></tr>'
        html += f'<tr><td style="padding: 5px;"><strong>Active Students:</strong></td><td>{active_students}</td></tr>'
        html += f'<tr><td style="padding: 5px;"><strong>Completed:</strong></td><td>{completed_enrollments}</td></tr>'
        html += f'<tr><td style="padding: 5px;"><strong>Modules:</strong></td><td>{total_modules}</td></tr>'
        html += f'<tr><td style="padding: 5px;"><strong>Total Lessons:</strong></td><td>{total_lessons}</td></tr>'
        html += f'</table></div>'
        return format_html(html)
    get_course_statistics.short_description = 'Course Statistics'
    
    def get_student_list(self, obj):
        from lessons.models import LessonCompletion
        enrollments = obj.enrollments.filter(is_active=True).select_related('student')
        
        html = '<div style="padding: 10px;">'
        html += '<table style="width: 100%; border-collapse: collapse;">'
        html += '<thead><tr style="background: #417690; color: white;">'
        html += '<th style="padding: 10px; text-align: left;">Student</th>'
        html += '<th style="padding: 10px; text-align: left;">Email</th>'
        html += '<th style="padding: 10px; text-align: center;">Progress</th>'
        html += '<th style="padding: 10px; text-align: center;">Lessons</th>'
        html += '<th style="padding: 10px; text-align: center;">Status</th>'
        html += '<th style="padding: 10px; text-align: center;">Enrolled</th>'
        html += '</tr></thead><tbody>'
        
        for enrollment in enrollments:
            total_lessons = sum(module.lessons.count() for module in obj.modules.all())
            completed_lessons = LessonCompletion.objects.filter(
                student=enrollment.student,
                lesson__module__course=obj
            ).count()
            
            status_color = 'green' if enrollment.completed else 'orange'
            status_text = 'Completed' if enrollment.completed else 'In Progress'
            
            html += f'<tr style="border-bottom: 1px solid #ddd;">'
            html += f'<td style="padding: 10px;"><strong>{enrollment.student.get_full_name() or enrollment.student.username}</strong></td>'
            html += f'<td style="padding: 10px;">{enrollment.student.email}</td>'
            html += f'<td style="padding: 10px; text-align: center;">{enrollment.progress:.0f}%</td>'
            html += f'<td style="padding: 10px; text-align: center;">{completed_lessons}/{total_lessons}</td>'
            html += f'<td style="padding: 10px; text-align: center;"><span style="color: {status_color}; font-weight: bold;">{status_text}</span></td>'
            html += f'<td style="padding: 10px; text-align: center;">{enrollment.enrollment_date.strftime("%Y-%m-%d")}</td>'
            html += '</tr>'
        
        if not enrollments:
            html += '<tr><td colspan="6" style="padding: 20px; text-align: center; color: #999;">No students enrolled yet</td></tr>'
        
        html += '</tbody></table></div>'
        return format_html(html)
    get_student_list.short_description = 'Enrolled Students Details'
    

    def assign_to_instructor(self, request, queryset):
        pass
    assign_to_instructor.short_description = 'Assign to instructor'
    
    def delete_courses(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count} courses deleted.')
    delete_courses.short_description = 'Delete selected courses'

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'lesson_count', 'order')
    list_filter = ('course',)
    search_fields = ('title', 'description', 'course__title')
    inlines = [LessonInline]
    list_per_page = 25
    
    def lesson_count(self, obj):
        return obj.lessons.count()
    lesson_count.short_description = 'Lessons'

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'get_course', 'has_video', 'has_attachment', 'order')
    list_filter = ('module__course',)
    search_fields = ('title', 'description', 'content')
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('module', 'title', 'description', 'order')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Media', {
            'fields': ('video_url', 'attachment')
        }),
    )
    
    def get_course(self, obj):
        return obj.module.course.title
    get_course.short_description = 'Course'
    
    def has_video(self, obj):
        return format_html(
            '<span style="color: {};">{}</span>',
            'green' if obj.video_url else 'red',
            '✓' if obj.video_url else '✗'
        )
    has_video.short_description = 'Video'
    
    def has_attachment(self, obj):
        return format_html(
            '<span style="color: {};">{}</span>',
            'green' if obj.attachment else 'red',
            '✓' if obj.attachment else '✗'
        )
    has_attachment.short_description = 'Attachment'
    


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'get_instructor', 'progress_bar', 'lesson_progress', 'completed', 'enrollment_date', 'is_active')
    list_filter = ('completed', 'is_active', 'enrollment_date', 'course', 'course__instructor')
    search_fields = ('student__username', 'student__email', 'course__title', 'course__instructor__username')
    date_hierarchy = 'enrollment_date'
    readonly_fields = ('enrollment_date', 'completion_date', 'get_detailed_progress', 'get_module_progress')
    list_per_page = 25
    
    fieldsets = (
        ('Enrollment Info', {
            'fields': ('student', 'course', 'is_active')
        }),
        ('Progress', {
            'fields': ('progress', 'completed', 'completion_date', 'get_detailed_progress')
        }),
        ('Module Progress', {
            'fields': ('get_module_progress',),
            'classes': ('wide',)
        }),
        ('Dates', {
            'fields': ('enrollment_date',)
        }),
    )
    
    actions = ['mark_completed', 'mark_incomplete', 'activate_enrollments', 'deactivate_enrollments']
    
    def get_instructor(self, obj):
        instructor = obj.course.instructor
        return format_html(
            '<a href="{}">{}</a>',
            f'/manage/instructors/{instructor.id}/',
            instructor.get_full_name() or instructor.username
        )
    get_instructor.short_description = 'Instructor'
    get_instructor.admin_order_field = 'course__instructor'
    
    def progress_bar(self, obj):
        color = 'green' if obj.completed else 'orange'
        return format_html(
            '<div style="width:100px; background-color:#f0f0f0; border-radius:5px;">' 
            '<div style="width:{}%; background-color:{}; height:20px; border-radius:5px; text-align:center; color:white; font-weight:bold;">{:.0f}%</div>' 
            '</div>',
            obj.progress, color, obj.progress
        )
    progress_bar.short_description = 'Progress'
    
    def lesson_progress(self, obj):
        from lessons.models import LessonCompletion
        total_lessons = sum(module.lessons.count() for module in obj.course.modules.all())
        completed_lessons = LessonCompletion.objects.filter(
            student=obj.student,
            lesson__module__course=obj.course
        ).count()
        return format_html(
            '<span style="font-weight: bold;">{}/{}</span>',
            completed_lessons, total_lessons
        )
    lesson_progress.short_description = 'Lessons'
    
    def get_detailed_progress(self, obj):
        from lessons.models import LessonCompletion
        total_lessons = sum(module.lessons.count() for module in obj.course.modules.all())
        completed_lessons = LessonCompletion.objects.filter(
            student=obj.student,
            lesson__module__course=obj.course
        ).count()
        
        html = f'<div style="padding: 10px; background: #f9f9f9; border-radius: 5px;">'
        html += f'<h3>Overall Progress: {completed_lessons}/{total_lessons} lessons completed ({obj.progress:.1f}%)</h3>'
        html += f'<p><strong>Student:</strong> {obj.student.get_full_name() or obj.student.username} ({obj.student.email})</p>'
        html += f'<p><strong>Course:</strong> {obj.course.title}</p>'
        html += f'<p><strong>Instructor:</strong> {obj.course.instructor.get_full_name() or obj.course.instructor.username}</p>'
        html += f'</div>'
        return format_html(html)
    get_detailed_progress.short_description = 'Detailed Progress'
    
    def get_module_progress(self, obj):
        from lessons.models import LessonCompletion
        
        html = '<div style="padding: 10px;">'
        html += '<table style="width: 100%; border-collapse: collapse;">'
        html += '<thead><tr style="background: #417690; color: white;">'
        html += '<th style="padding: 10px; text-align: left;">Module</th>'
        html += '<th style="padding: 10px; text-align: center;">Lessons</th>'
        html += '<th style="padding: 10px; text-align: center;">Completed</th>'
        html += '<th style="padding: 10px; text-align: center;">Progress</th>'
        html += '<th style="padding: 10px; text-align: left;">Completed Lessons</th>'
        html += '</tr></thead><tbody>'
        
        for module in obj.course.modules.all():
            total = module.lessons.count()
            completed_lesson_ids = LessonCompletion.objects.filter(
                student=obj.student,
                lesson__module=module
            ).values_list('lesson_id', flat=True)
            completed = len(completed_lesson_ids)
            progress = (completed / total * 100) if total > 0 else 0
            
            completed_lessons = module.lessons.filter(id__in=completed_lesson_ids)
            lesson_names = ', '.join([lesson.title for lesson in completed_lessons]) or 'None'
            
            color = '#d4edda' if progress == 100 else '#fff3cd' if progress > 0 else '#f8d7da'
            html += f'<tr style="background: {color}; border-bottom: 1px solid #ddd;">'
            html += f'<td style="padding: 10px;"><strong>{module.title}</strong></td>'
            html += f'<td style="padding: 10px; text-align: center;">{total}</td>'
            html += f'<td style="padding: 10px; text-align: center;">{completed}</td>'
            html += f'<td style="padding: 10px; text-align: center;"><strong>{progress:.0f}%</strong></td>'
            html += f'<td style="padding: 10px; font-size: 12px;">{lesson_names}</td>'
            html += '</tr>'
        
        html += '</tbody></table></div>'
        return format_html(html)
    get_module_progress.short_description = 'Module-wise Progress'
    
    def mark_completed(self, request, queryset):
        count = queryset.update(completed=True, progress=100)
        self.message_user(request, f'{count} enrollments marked as completed.')
    mark_completed.short_description = 'Mark as completed'
    
    def mark_incomplete(self, request, queryset):
        count = queryset.update(completed=False)
        self.message_user(request, f'{count} enrollments marked as incomplete.')
    mark_incomplete.short_description = 'Mark as incomplete'
    
    def activate_enrollments(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} enrollments activated.')
    activate_enrollments.short_description = 'Activate enrollments'
    
    def deactivate_enrollments(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} enrollments deactivated.')
    deactivate_enrollments.short_description = 'Deactivate enrollments'


@admin.register(CourseNote)
class CourseNoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'uploaded_by', 'uploaded_at')
    list_filter = ('course', 'uploaded_at')
    search_fields = ('title', 'course__title', 'uploaded_by__username')

from django.contrib import admin
from django.utils.html import format_html
from .models import LessonCompletion, LessonDoubt, DoubtResponse

@admin.register(LessonCompletion)
class LessonCompletionAdmin(admin.ModelAdmin):
    list_display = ('student', 'get_student_email', 'lesson', 'get_module', 'get_course', 'get_instructor', 'completed_at')
    list_filter = ('completed_at', 'lesson__module__course', 'lesson__module__course__instructor', 'lesson__module')
    search_fields = ('student__username', 'student__email', 'lesson__title', 'lesson__module__course__title', 'lesson__module__course__instructor__username')
    date_hierarchy = 'completed_at'
    readonly_fields = ('completed_at', 'get_completion_details')
    list_per_page = 25
    
    fieldsets = (
        ('Completion Info', {
            'fields': ('student', 'lesson', 'completed_at')
        }),
        ('Details', {
            'fields': ('get_completion_details',),
            'classes': ('wide',)
        }),
    )
    
    def get_student_email(self, obj):
        return obj.student.email
    get_student_email.short_description = 'Student Email'
    
    def get_module(self, obj):
        return obj.lesson.module.title
    get_module.short_description = 'Module'
    
    def get_course(self, obj):
        return obj.lesson.module.course.title
    get_course.short_description = 'Course'
    
    def get_instructor(self, obj):
        instructor = obj.lesson.module.course.instructor
        return instructor.get_full_name() or instructor.username
    get_instructor.short_description = 'Instructor'
    
    def get_completion_details(self, obj):
        course = obj.lesson.module.course
        total_lessons = sum(module.lessons.count() for module in course.modules.all())
        completed_lessons = LessonCompletion.objects.filter(
            student=obj.student,
            lesson__module__course=course
        ).count()
        progress = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        html = '<div style="padding: 15px; background: #f9f9f9; border-radius: 5px;">'
        html += f'<h3>Lesson Completion Details</h3>'
        html += f'<p><strong>Student:</strong> {obj.student.get_full_name() or obj.student.username} ({obj.student.email})</p>'
        html += f'<p><strong>Lesson:</strong> {obj.lesson.title}</p>'
        html += f'<p><strong>Module:</strong> {obj.lesson.module.title}</p>'
        html += f'<p><strong>Course:</strong> {course.title}</p>'
        html += f'<p><strong>Instructor:</strong> {course.instructor.get_full_name() or course.instructor.username}</p>'
        html += f'<p><strong>Course Progress:</strong> {completed_lessons}/{total_lessons} lessons ({progress:.1f}%)</p>'
        html += f'<p><strong>Completed At:</strong> {obj.completed_at.strftime("%Y-%m-%d %H:%M:%S")}</p>'
        html += '</div>'
        return format_html(html)
    get_completion_details.short_description = 'Completion Details'
    
    actions = ['delete_completions']
    
    def delete_completions(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count} lesson completions deleted.')
    delete_completions.short_description = 'Delete selected completions'

@admin.register(LessonDoubt)
class LessonDoubtAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'get_course', 'is_resolved', 'created_at')
    list_filter = ('is_resolved', 'created_at', 'lesson__module__course')
    search_fields = ('student__username', 'question', 'lesson__title')
    readonly_fields = ('created_at',)
    
    def get_course(self, obj):
        return obj.lesson.module.course.title
    get_course.short_description = 'Course'

@admin.register(DoubtResponse)
class DoubtResponseAdmin(admin.ModelAdmin):
    list_display = ('instructor', 'get_student', 'get_lesson', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('instructor__username', 'response', 'doubt__question')
    readonly_fields = ('created_at',)
    
    def get_student(self, obj):
        return obj.doubt.student.username
    get_student.short_description = 'Student'
    
    def get_lesson(self, obj):
        return obj.doubt.lesson.title
    get_lesson.short_description = 'Lesson'

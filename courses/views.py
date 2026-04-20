from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db import models
from django.db import transaction
import json
import socket
import urllib.error
import urllib.request
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST


from .models import Course, Lesson, Enrollment, Module, Category, CourseNote, VideoNote
from .forms import CourseForm, LessonForm, CourseNoteForm, VideoNoteForm
from .progress import get_module_access_map, get_completed_quiz_ids
from accounts.decorators import student_required, instructor_required


def execute_with_compiler(source_code, language_key, stdin_text=''):
    language_map = {
        'python': {
            'language': 'python',
            'file_name': 'main.py',
        },
        'javascript': {
            'language': 'javascript',
            'file_name': 'main.js',
        },
    }

    compiler_config = language_map[language_key]
    api_url = settings.COMPILER_API_URL
    api_key = settings.COMPILER_API_KEY

    if not api_key:
        raise RuntimeError('Compiler API key is missing. Set COMPILER_API_KEY in settings.py or environment variables.')

    payload = json.dumps({
        'language': compiler_config['language'],
        'stdin': stdin_text,
        'files': [
            {
                'name': compiler_config['file_name'],
                'content': source_code,
            }
        ],
    }).encode('utf-8')

    compiler_request = urllib.request.Request(
        api_url,
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
            'X-API-Key': api_key,
        },
        method='POST',
    )

    try:
        with urllib.request.urlopen(compiler_request, timeout=20) as response:
            result = json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode('utf-8', errors='ignore')
        raise RuntimeError(f'Compiler service returned HTTP {exc.code}. {detail}'.strip()) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError('Compiler service is currently unreachable.') from exc
    except socket.timeout as exc:
        raise RuntimeError('Compiler service timed out. Please try again.') from exc

    if isinstance(result, list):
        result = result[0] if result else {}

    if result.get('status') == 'failed':
        raise RuntimeError(result.get('error') or 'Compiler service failed to process the request.')

    return {
        'stdout': result.get('stdout') or '',
        'stderr': result.get('stderr') or '',
        'compile_output': result.get('exception') or result.get('error') or '',
        'status': result.get('status') or 'Unknown',
    }

# A mixin to ensure that the user is an instructor
class InstructorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_instructor

# A mixin to ensure that the user is an admin
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin

# A mixin to ensure that the instructor owns the course or user is admin
class CourseOwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        course = get_object_or_404(Course, pk=self.kwargs['pk'])
        return self.request.user == course.instructor or self.request.user.is_admin or self.request.user.is_admin

# --- Course Views ---

class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        category_id = self.request.GET.get('category')
        if query:
            queryset = queryset.filter(
                models.Q(title__icontains=query) |
                models.Q(description__icontains=query) |
                models.Q(instructor__username__icontains=query)
            )
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category', '')
        return context

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for module in self.object.modules.all():
            module.normalize_lesson_order()
        modules = list(self.object.modules.prefetch_related('lessons', 'quizzes').all())
        context['modules'] = modules

        if self.request.user.is_authenticated:
            enrollment = Enrollment.objects.filter(
                course=self.object, student=self.request.user, is_active=True
            ).first()
            context['is_enrolled'] = enrollment is not None
            context['enrollment'] = enrollment
            
            # Get completed lessons and quizzes for tick marks
            if enrollment and self.request.user.is_student:
                module_access, completed_lessons = get_module_access_map(self.object, self.request.user)
                completed_quizzes = get_completed_quiz_ids(self.object, self.request.user)
                context['completed_lessons'] = completed_lessons
                context['completed_quizzes'] = completed_quizzes

                for module in modules:
                    status = module_access.get(module.id, {'unlocked': True, 'completed': False})
                    module.is_unlocked = status['unlocked']
                    module.is_completed = status['completed']
                    module.is_locked = not status['unlocked']

                    for lesson in module.lessons.all():
                        lesson.is_accessible = status['unlocked']

                    for quiz in module.quizzes.all():
                        quiz.is_accessible = status['unlocked']
            else:
                context['completed_lessons'] = set()
                context['completed_quizzes'] = set()
                for module in modules:
                    module.is_unlocked = True
                    module.is_completed = False
                    module.is_locked = False
                    for lesson in module.lessons.all():
                        lesson.is_accessible = True
                    for quiz in module.quizzes.all():
                        quiz.is_accessible = True

        else:
            context['is_enrolled'] = False
            context['enrollment'] = None
            context['completed_lessons'] = set()
            context['completed_quizzes'] = set()
            for module in modules:
                module.is_unlocked = True
                module.is_completed = False
                module.is_locked = False
                for lesson in module.lessons.all():
                    lesson.is_accessible = True
                for quiz in module.quizzes.all():
                    quiz.is_accessible = True
        
        # Reviews
        from reviews.models import Review
        reviews = self.object.reviews.all()
        context['reviews'] = reviews
        context['avg_rating'] = reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0
        context['course_notes'] = self.object.notes.select_related('uploaded_by').all()
        context['can_upload_notes'] = (
            self.request.user.is_authenticated and
            (self.request.user == self.object.instructor or self.request.user.is_admin)
        )
        if context['can_upload_notes']:
            context['note_form'] = CourseNoteForm()
        if self.request.user.is_authenticated:
            context['user_review'] = reviews.filter(student=self.request.user).first()
        return context

class CourseCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Automatically create a default module for the new course
        Module.objects.create(
            course=self.object,
            title="Module 1",
            description="Default module for the course",
            order=1
        )
        
        messages.success(self.request, "Course created successfully with a default module!")
        return response

    def get_success_url(self):
        return reverse_lazy('courses:course_detail', kwargs={'pk': self.object.pk})

class CourseUpdateView(LoginRequiredMixin, CourseOwnerRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'

    def form_valid(self, form):
        messages.success(self.request, "Course updated successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('courses:course_detail', kwargs={'pk': self.object.pk})

# --- Lesson Views ---

class LessonCreateView(LoginRequiredMixin, CreateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'lessons/lesson_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
        kwargs['course'] = course
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
        context['course'] = course
        context['has_modules'] = course.modules.exists()
        context['lesson'] = getattr(self, 'object', None)
        return context

    def form_valid(self, form):
        course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
        if not (self.request.user == course.instructor or self.request.user.is_admin):
            messages.error(self.request, "You are not authorized to add lessons to this course.")
            return redirect('courses:course_detail', pk=course.pk)
        
        if not course.modules.exists():
            messages.error(self.request, "Please create a module first before adding lessons.")
            return redirect('courses:module_create', course_pk=course.pk)
        
        messages.success(self.request, "Lesson created successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('courses:course_detail', kwargs={'pk': self.kwargs['course_pk']})

class LessonUpdateView(LoginRequiredMixin, UpdateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'lessons/lesson_form.html'

    def get_queryset(self):
        if self.request.user.is_admin:
            return super().get_queryset()
        return super().get_queryset().filter(module__course__instructor=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['course'] = self.get_object().module.course
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.object.module.course
        context['lesson'] = self.object
        return context

    def form_valid(self, form):
        messages.success(self.request, "Lesson updated successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('courses:course_detail', kwargs={'pk': self.object.module.course.pk})

class LessonDeleteView(LoginRequiredMixin, DeleteView):
    model = Lesson
    template_name = 'lessons/lesson_confirm_delete.html'

    def get_queryset(self):
        if self.request.user.is_admin:
            return super().get_queryset()
        return super().get_queryset().filter(module__course__instructor=self.request.user)

    def form_valid(self, form):
        self.object = self.get_object()
        module = self.object.module

        with transaction.atomic():
            response = super().form_valid(form)

            module.normalize_lesson_order()

        messages.success(self.request, "Lesson deleted successfully and lesson numbers were updated.")
        return response

    def get_success_url(self):
        from django.urls import reverse
        return reverse('courses:course_detail', kwargs={'pk': self.object.module.course.pk})

@login_required
@student_required
def enroll_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course
    )
    if created:
        # Send enrollment confirmation email
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = f'Enrollment Confirmation - {course.title}'
        message = f'''Dear {request.user.get_full_name() or request.user.username},

Congratulations! You have successfully enrolled in "{course.title}".

Course Details:
- Title: {course.title}
- Instructor: {course.instructor.get_full_name() or course.instructor.username}
- Enrolled on: {enrollment.enrollment_date.strftime("%B %d, %Y")}

You can now access all course materials, lessons, and quizzes.

Start learning: {settings.SITE_URL}/courses/{course.pk}/

Best regards,
LMS Team
'''
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@lms.com',
                [request.user.email],
                fail_silently=True,
            )
        except Exception as e:
            pass  # Don't fail enrollment if email fails
        
        messages.success(request, f"You have successfully enrolled in {course.title}! A confirmation email has been sent.")
    else:
        messages.info(request, f"You are already enrolled in {course.title}.")
    return redirect('courses:course_detail', pk=course.pk)

@login_required
def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    course = lesson.module.course
    
    # Check if user is enrolled or is the instructor
    is_enrolled = Enrollment.objects.filter(student=request.user, course=course, is_active=True).exists()
    is_instructor = request.user == course.instructor
    
    if not (is_enrolled or is_instructor or request.user.is_admin):
        if course.course_access_type == 'paid':
            messages.error(request, "Complete the payment for this course to view lessons.")
        else:
            messages.error(request, "You must be enrolled in this course to view lessons.")
        return redirect('courses:course_detail', pk=course.pk)

    if is_enrolled and request.user.is_student:
        module_access, _ = get_module_access_map(course, request.user)
        if not module_access.get(lesson.module_id, {'unlocked': True})['unlocked']:
            messages.error(request, "Complete the previous module to unlock this one.")
            return redirect('courses:course_detail', pk=course.pk)
    
    # Get lesson completion status
    from lessons.models import LessonCompletion
    from quizzes.models import QuizAttempt
    is_completed = LessonCompletion.objects.filter(student=request.user, lesson=lesson).exists()
    
    # Check if lesson has quizzes and if they're completed
    lesson_quizzes = lesson.module.quizzes.all()
    quizzes_completed = True
    if lesson_quizzes.exists():
        for quiz in lesson_quizzes:
            if not QuizAttempt.objects.filter(
                student=request.user,
                quiz=quiz,
                completed_at__isnull=False,
                passed=True,
            ).exists():
                quizzes_completed = False
                break
    
    context = {
        'lesson': lesson,
        'course': course,
        'is_completed': is_completed,
        'quizzes_completed': quizzes_completed,
        'has_quizzes': lesson_quizzes.exists(),
        'video_notes': VideoNote.objects.filter(lesson=lesson).select_related('created_by'),
        'video_note_form': VideoNoteForm(),
        'can_manage_video_notes': is_instructor or request.user.is_admin,
    }
    return render(request, 'lessons/lesson_detail.html', context)


@login_required
def add_video_note(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    course = lesson.module.course

    if not (request.user == course.instructor or request.user.is_admin):
        messages.error(request, "Only the instructor or admin can add second-wise video notes.")
        return redirect('courses:lesson_detail', pk=lesson.pk)

    if request.method != 'POST':
        return redirect('courses:lesson_detail', pk=lesson.pk)

    form = VideoNoteForm(request.POST)
    if form.is_valid():
        video_note = form.save(commit=False)
        video_note.lesson = lesson
        video_note.created_by = request.user
        video_note.save()
        messages.success(request, "Video note added to the lesson.")
    else:
        messages.error(request, "Could not save the video note. Please check the form and try again.")

    return redirect('courses:lesson_detail', pk=lesson.pk)


@login_required
def manage_video_notes(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    course = lesson.module.course

    if not (request.user == course.instructor or request.user.is_admin):
        messages.error(request, "Only the instructor or admin can manage video notes.")
        return redirect('courses:lesson_detail', pk=lesson.pk)

    if request.method == 'POST':
        form = VideoNoteForm(request.POST)
        if form.is_valid():
            video_note = form.save(commit=False)
            video_note.lesson = lesson
            video_note.created_by = request.user
            video_note.save()
            messages.success(request, "Video note added successfully.")
            return redirect('courses:manage_video_notes', pk=lesson.pk)
        messages.error(request, "Could not save the video note. Please check the form and try again.")
    else:
        form = VideoNoteForm()

    context = {
        'lesson': lesson,
        'course': course,
        'video_notes': VideoNote.objects.filter(lesson=lesson).select_related('created_by'),
        'video_note_form': form,
    }
    return render(request, 'lessons/manage_video_notes.html', context)


@login_required
def delete_video_note(request, lesson_pk, note_pk):
    lesson = get_object_or_404(Lesson, pk=lesson_pk)
    course = lesson.module.course

    if not (request.user == course.instructor or request.user.is_admin):
        messages.error(request, "Only the instructor or admin can delete video notes.")
        return redirect('courses:lesson_detail', pk=lesson.pk)

    if request.method != 'POST':
        return redirect('courses:manage_video_notes', pk=lesson.pk)

    video_note = get_object_or_404(VideoNote, pk=note_pk, lesson=lesson)
    video_note.delete()
    messages.success(request, "Video note deleted successfully.")
    return redirect('courses:manage_video_notes', pk=lesson.pk)

@login_required
@student_required
def mark_lesson_complete(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    course = lesson.module.course
    
    # Verify enrollment
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course, is_active=True)
    
    from lessons.models import LessonCompletion
    completion, created = LessonCompletion.objects.get_or_create(
        student=request.user,
        lesson=lesson
    )
    
    if created:
        messages.success(request, f"Lesson '{lesson.title}' marked as complete!")
        enrollment.update_progress()
    else:
        messages.info(request, "Lesson already marked as complete.")
    
    return redirect('courses:lesson_detail', pk=lesson.pk)

@login_required
@instructor_required
def manage_course_students(request, pk):
    course = get_object_or_404(Course, pk=pk, instructor=request.user)
    enrollments = Enrollment.objects.filter(course=course).select_related('student').order_by('-enrollment_date')
    
    for enrollment in enrollments:
        enrollment.update_progress()
    
    context = {
        'course': course,
        'enrollments': enrollments,
    }
    return render(request, 'courses/manage_students.html', context)

@login_required
@instructor_required
def toggle_student_enrollment(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, pk=enrollment_id, course__instructor=request.user)
    enrollment.is_active = not enrollment.is_active
    enrollment.save()
    status = "activated" if enrollment.is_active else "deactivated"
    messages.success(request, f"Student enrollment {status} successfully!")
    return redirect('courses:manage_students', pk=enrollment.course.pk)


@login_required
def create_module(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    
    # Check if user is instructor of this course or admin
    if not (request.user == course.instructor or request.user.is_admin):
        messages.error(request, "You don't have permission to add modules to this course.")
        return redirect('courses:course_detail', pk=course.pk)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        order = Module.objects.filter(course=course).count() + 1
        
        Module.objects.create(
            course=course,
            title=title,
            description=description,
            order=order
        )
        messages.success(request, f"Module '{title}' created successfully!")
        return redirect('courses:course_detail', pk=course.pk)
    
    context = {
        'course': course,
        'module_count': Module.objects.filter(course=course).count()
    }
    return render(request, 'courses/module_form.html', context)


@login_required
def upload_course_note(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if not (request.user == course.instructor or request.user.is_admin):
        messages.error(request, "You don't have permission to upload notes for this course.")
        return redirect('courses:course_detail', pk=course.pk)

    if request.method != 'POST':
        return redirect('courses:course_detail', pk=course.pk)

    form = CourseNoteForm(request.POST, request.FILES)
    if form.is_valid():
        course_note = form.save(commit=False)
        course_note.course = course
        course_note.uploaded_by = request.user
        if not course_note.title:
            course_note.title = course_note.file.name.split('/')[-1]
        course_note.save()
        messages.success(request, "Course note uploaded successfully.")
    else:
        messages.error(request, "Could not upload note. Please check the form and file.")

    return redirect('courses:course_detail', pk=course.pk)

@login_required
@instructor_required
def instructor_manage_all_students(request):
    courses = Course.objects.filter(instructor=request.user)
    enrollments = Enrollment.objects.filter(course__in=courses).select_related('student', 'course').order_by('-enrollment_date')
    
    from lessons.models import LessonCompletion
    from quizzes.models import QuizAttempt
    from certificates.models import Certificate
    
    student_data = []
    for enrollment in enrollments:
        enrollment.update_progress()
        
        completed_lessons = LessonCompletion.objects.filter(
            student=enrollment.student,
            lesson__module__course=enrollment.course
        ).count()
        
        total_lessons = Lesson.objects.filter(module__course=enrollment.course).count()
        
        quiz_attempts = QuizAttempt.objects.filter(
            student=enrollment.student,
            quiz__module__course=enrollment.course
        ).count()
        
        certificate = Certificate.objects.filter(enrollment=enrollment).first()
        
        student_data.append({
            'enrollment': enrollment,
            'completed_lessons': completed_lessons,
            'total_lessons': total_lessons,
            'quiz_attempts': quiz_attempts,
            'certificate': certificate,
        })
    
    context = {
        'student_data': student_data,
        'total_students': enrollments.count(),
    }
    return render(request, 'courses/instructor_manage_all_students.html', context)


@login_required
@require_POST
def run_lesson_code(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    course = lesson.module.course

    is_enrolled = Enrollment.objects.filter(
        student=request.user,
        course=course,
        is_active=True
    ).exists()
    is_instructor = request.user == course.instructor

    if not (is_enrolled or is_instructor or request.user.is_admin):
        return JsonResponse({'error': 'You are not allowed to run code for this lesson.'}, status=403)

    if not lesson.has_coding_lab:
        return JsonResponse({'error': 'Coding lab is not enabled for this lesson.'}, status=400)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request format.'}, status=400)

    source_code = (data.get('code') or '').strip()
    stdin_text = data.get('stdin') or ''
    language = data.get('language') or lesson.coding_language

    allowed_languages = {'python', 'javascript'}

    if language not in allowed_languages:
        return JsonResponse({'error': 'Unsupported language selected.'}, status=400)

    if len(source_code) == 0:
        return JsonResponse({'error': 'Please enter code before running.'}, status=400)

    if len(source_code) > 10000:
        return JsonResponse({'error': 'Code is too long.'}, status=400)

    try:
        result = execute_with_compiler(source_code, language, stdin_text)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({
        'stdout': result.get('stdout') or '',
        'stderr': result.get('stderr') or '',
        'compile_output': result.get('compile_output') or '',
        'status': result.get('status') or 'Unknown',
    })


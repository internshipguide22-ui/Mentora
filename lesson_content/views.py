from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from courses.models import Lesson
from .models import VideoContent, TextContent, QuizContent, AssignmentContent
from .forms import VideoContentForm, TextContentForm, QuizContentForm, AssignmentContentForm

class ContentOwnerMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        lesson = get_object_or_404(Lesson, pk=self.kwargs['lesson_pk'])
        if lesson.module.course.instructor != request.user:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        lesson_pk = self.kwargs['lesson_pk']
        return reverse_lazy('courses:lesson_detail', kwargs={'pk': lesson_pk})

# Video Content Views
class VideoContentCreateView(ContentOwnerMixin, CreateView):
    model = VideoContent
    form_class = VideoContentForm
    template_name = 'lesson_content/content_form.html'

    def form_valid(self, form):
        lesson = get_object_or_404(Lesson, pk=self.kwargs['lesson_pk'])
        form.instance.lesson = lesson
        return super().form_valid(form)

class VideoContentUpdateView(ContentOwnerMixin, UpdateView):
    model = VideoContent
    form_class = VideoContentForm
    template_name = 'lesson_content/content_form.html'

class VideoContentDeleteView(ContentOwnerMixin, DeleteView):
    model = VideoContent
    template_name = 'lesson_content/content_confirm_delete.html'

# Text Content Views
class TextContentCreateView(ContentOwnerMixin, CreateView):
    model = TextContent
    form_class = TextContentForm
    template_name = 'lesson_content/content_form.html'

    def form_valid(self, form):
        lesson = get_object_or_404(Lesson, pk=self.kwargs['lesson_pk'])
        form.instance.lesson = lesson
        return super().form_valid(form)

class TextContentUpdateView(ContentOwnerMixin, UpdateView):
    model = TextContent
    form_class = TextContentForm
    template_name = 'lesson_content/content_form.html'

class TextContentDeleteView(ContentOwnerMixin, DeleteView):
    model = TextContent
    template_name = 'lesson_content/content_confirm_delete.html'

# Quiz Content Views
class QuizContentCreateView(ContentOwnerMixin, CreateView):
    model = QuizContent
    form_class = QuizContentForm
    template_name = 'lesson_content/content_form.html'

    def form_valid(self, form):
        lesson = get_object_or_404(Lesson, pk=self.kwargs['lesson_pk'])
        form.instance.lesson = lesson
        return super().form_valid(form)

class QuizContentUpdateView(ContentOwnerMixin, UpdateView):
    model = QuizContent
    form_class = QuizContentForm
    template_name = 'lesson_content/content_form.html'

class QuizContentDeleteView(ContentOwnerMixin, DeleteView):
    model = QuizContent
    template_name = 'lesson_content/content_confirm_delete.html'

# Assignment Content Views
class AssignmentContentCreateView(ContentOwnerMixin, CreateView):
    model = AssignmentContent
    form_class = AssignmentContentForm
    template_name = 'lesson_content/content_form.html'

    def form_valid(self, form):
        lesson = get_object_or_404(Lesson, pk=self.kwargs['lesson_pk'])
        form.instance.lesson = lesson
        return super().form_valid(form)

class AssignmentContentUpdateView(ContentOwnerMixin, UpdateView):
    model = AssignmentContent
    form_class = AssignmentContentForm
    template_name = 'lesson_content/content_form.html'

class AssignmentContentDeleteView(ContentOwnerMixin, DeleteView):
    model = AssignmentContent
    template_name = 'lesson_content/content_confirm_delete.html'
